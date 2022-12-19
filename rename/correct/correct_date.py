import re
import local_config as cfg

from . import CorrectInterface
from utils import extract_task_id


class CorrectDate(CorrectInterface):
    """ [year(start, end), month(start, end), day(start, end)] """
    date_dict = {
        "22\d{4}": [(0, 2), (2, 4), (4, 6)],
        "2022\d{4}": [(2, 4), (4, 6), (6, 8)],
        "2022-\d{2}-\d{2}": [(2, 4), (5, 7), (8, 10)],
        "2022_\d{2}_\d{2}": [(2, 4), (5, 7), (8, 10)],
    }

    time_list = [
        " \d{2}_\d{2}_\d{2}",
        " \d{2} \d{2} \d{2}"
    ]

    manual = {
        "2200906": "220906",
        "229020": "220920"
    }

    @classmethod
    def execute(cls, file_name, data_info):
        """
        yyyy-mm-dd -> yymmdd
        ^*hh mm ss$ -> ^*yymmdd$
        """
        cls.data_info = data_info

        # date formatting
        file_name = cls.__edit_date_format(file_name)

        # remove hh mm ss
        for time_format in cls.time_list:
            time = cls.find_date(file_name, time_format)
            if time is None:
                continue
            file_name = file_name.replace(time, "")

        # 수동 수정
        file_name = cls.__correct_manually(file_name)

        # 날짜가 없으면 추가
        if not cls.__is_date_in(file_name):
            file_name = cls.__add_date(file_name)

        # 날짜 범위 수정
        file_name = cls.__correct_date_range(file_name)

        # validate & #
        date = cls.__extract_date_part(file_name)
        try:
            cls.__validate_date_format(date)
        except Exception as e:
            print(file_name)
            raise e
        return file_name

    @classmethod
    def __correct_manually(cls, file_name):
        for old, new in cls.manual.items():
            if old in file_name:
                file_name = file_name.replace(old, new)
        return file_name

    @classmethod
    def __edit_date_format(cls, input):
        for date_format, indices in cls.date_dict.items():
            date = cls.find_date(input, date_format)  # None or Date
            if date is None:
                continue
            new_date = "".join([date[i[0]:i[1]] for i in indices])
            input = input.replace(date, new_date)
        return input

    @classmethod
    def __is_date_in(cls, file_name: str) -> bool:
        check_every_format = []
        for date_format in cls.date_dict.keys():
            finder = re.compile(date_format)
            date = finder.search(file_name)
            check_every_format.append(date is not None)
        return any(check_every_format)

    @classmethod
    def __correct_date_range(cls, file_name):
        date = cls.find_date(file_name, "22\d{4}")
        if date is None:
            raise Exception(f"{file_name} 에 6자리 유효한 날짜 형식이 없습니다.")

        # check
        finder = re.compile(cfg.DATE_FORMAT)
        find = finder.search(file_name)
        if find is not None:
            return file_name
            # raise Exception(f"{file_name}에 유효한 날짜 형식(범위 포함)이 없습니다.")

        # edit wrong date to complete date
        complete_date = cls.__find_complete_date(file_name)
        file_name = file_name.replace(date, complete_date)
        return file_name

    @classmethod
    def __add_date(cls, file_name):
        """ 파일명에 날짜 추가 """
        complete_date = cls.__find_complete_date(file_name)
        delimiter = "."
        splitted = file_name.split(delimiter)
        return f"{delimiter.join(splitted[:-1])}_{complete_date}.{splitted[-1]}"

    @ classmethod
    def __find_complete_date(cls, file_name):
        task_id = extract_task_id(file_name)
        complete_date = cls.data_info[cls.data_info["number"]
                                      == task_id]["complete_date"]
        if len(complete_date) == 0:
            raise Exception(f"과제 번호({task_id})가 master table에 없습니다.")
        if len(complete_date) > 1:
            raise Exception(f"과제 번호({task_id})가 master table에 여러 개 들어있습니다.")
        complete_date = complete_date.tolist()[0]
        complete_date = cls.__edit_date_format(complete_date)
        return complete_date

    @classmethod
    def __extract_date_part(cls, file_name):
        return file_name.split("_")[-1].split(".")[0]

    @ classmethod
    def find_date(cls, date_part, date_format):
        date_finder = re.compile(date_format)
        date = date_finder.search(date_part)
        if date is None:
            return None
        return date.group()

    @ classmethod
    def __validate_date_format(cls, date):
        date_finder = re.compile(cfg.DATE_FORMAT)
        if date_finder.match(date) is None:
            raise Exception("날짜 형식이 완벽하게 수정되지 않았습니다.")
