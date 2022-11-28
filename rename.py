from copy import deepcopy
import pandas as pd
from abc import ABCMeta, abstractmethod
import shutil
from tqdm import tqdm
import re
import os

from utils import path_join, extract_task_id, validate_name_format
import local_config as cfg
from collections import OrderedDict

# 메타클래스 정의(클래스를 생성하는 클래스)

"""
[
    'AddTaskId',
    'CorrectWrongId',
    'AddTaskCode',
    'CorrectTaskId',
    'CorrectBracket',
    'CorrectDate',
    'CorrectResultType',
    'CorrectSequence',
    'CorrectSpace',
    'CorrectDelimiter'
]
"""


class RegistryMetaClass(type):
    def __new__(cls, name, bases, attrs):
        # 클래스를 생성한다.
        new_cls = type.__new__(cls, name, bases, attrs)
        # 클래스의 속성에 REGISTRY가 있다면
        # bases 내에 RegistryMetaClass를 메타 클래스로 활용한 슈퍼 클래스가 있다는 의미로 간주하여
        if hasattr(new_cls, "REGISTRY"):
            # (다중 상속에도 원하는 방식으로 동작하도록)
            for base in bases:
                if hasattr(base, "REGISTRY"):
                    # REGISTRY에 생성된 클래스를 등록한다.
                    base.REGISTRY[name] = new_cls
        # REGISTRY 속성이 없다면
        else:
            # RegistryMetaClass가 메타 클래스로 활용되었으므로 REGISTRY 속성을 부여한다.
            new_cls.REGISTRY = OrderedDict()
        return new_cls

    def execute(self, msg: str = ""):
        raise NotImplementedError


class Correct(metaclass=RegistryMetaClass):
    data_info = pd.read_csv(cfg.DATA_INFO_PATH, encoding="cp949")

    def __init__(self, file_list: list):
        self.old_file_list = file_list
        self.new_file_list = {}

    def execute(self, p=False):
        if len(self.new_file_list):
            print("이미 execute를 실행했습니다.")
            return

        print(self.REGISTRY.keys())

        for file_path in self.old_file_list:
            file_name = file_path.split("/")[-1]
            self.new_file_list[file_path] = self.correct(file_name, p=p)

    def rename(self, root, p=False, progress_bar: bool = True):
        if not os.path.exists(root):
            print(f"{root} 경로가 존재하지 않습니다.")
            return

        file_list = list(filter(lambda x: x.split(
            ".")[-1] in ["csv", "xlsx"], os.listdir(root)))
        if progress_bar:
            bar = tqdm(file_list,
                       total=len(file_list))
        else:
            bar = file_list

        for old_file in bar:
            old_path = path_join(root, old_file)
            new_path = path_join(root, self.correct(old_file, p=p))
            if os.path.exists(new_path):
                os.remove(new_path)
                continue
            os.rename(old_path, new_path)

    def copy_to(self, root, overwrite=False, progress_bar: bool = True):
        """ 기존 파일의 수정 버전을 root 하위에 옮긴다. """
        if len(self.new_file_list) == 0:
            print("new_file_list가 비어있습니다. execute 메서드를 먼저 실행해주시기 바랍니다.")
            return

        if not os.path.exists(root):
            print(f"{root} 경로가 존재하지 않습니다.")
            return

        file_list = deepcopy(self.new_file_list)
        print("전체 파일 수:", len(file_list))
        existed_num = 0
        remove_keys = []
        for key, new_path in file_list.items():
            if os.path.exists(path_join(root, new_path)):
                existed_num += 1
                if not overwrite:
                    remove_keys.append(key)

        if not overwrite:
            for key in remove_keys:
                del(file_list[key])

        print("이름이 이미 수정된 파일 수:", existed_num)
        print("새로운 파일 수:", len(self.new_file_list) - existed_num)

        if progress_bar:
            bar = tqdm(file_list.items(),
                       total=len(file_list))
        else:
            bar = file_list.items()

        for old_path, new_name in bar:
            new_path = path_join(root, new_name)
            if not os.path.exists(new_path):
                shutil.copy(old_path, new_path)

    def correct(self, file_path: str, p=True) -> str:
        file_name = file_path.split("\\")[-1]
        prev_name = deepcopy(file_name)
        # if file_path == "페르소나 대화 데이터_형식오류목록_2022-08-25 14_07_54.csv":
        #     import pdb
        # pdb.set_trace()
        for name, sub_class in self.REGISTRY.items():
            file_name = sub_class.execute(file_name)
        try:
            validate_name_format(file_name)
        except Exception as e:
            print("before:", file_path)
            print("after:", file_name)
            raise e

        if p and prev_name != file_name:
            print("기존: " + prev_name)
            print("변경: " + file_name)
            print()
        return file_path.replace(prev_name, file_name)


class AddTaskId(Correct):
    """
    페르소나 대화 데이터_형식오류목록_2022-08-25
    -> 아이디 추가
    """
    @classmethod
    def execute(cls, file_name):
        file_name = cls.__correct_task_id(file_name)
        if cls.__has_task_id(file_name):
            return file_name
        file_name = cls.__add_task_id(file_name)
        return file_name

    @classmethod
    def __has_task_id(cls, file_name) -> bool:
        format = "\d-\d{3}-\d{3}"
        finder = re.compile(format)
        check = finder.search(file_name)
        return check is not None

    @classmethod
    def __correct_task_id(cls, file_name) -> bool:
        """
        2-49-175 -> 2-049-175
        """
        format = "\d-\d{2}-\d{3}"
        finder = re.compile(format)
        check = finder.search(file_name)
        if check is None:
            return file_name
        s, e = check.span()
        old = file_name[s:e]
        new = old[:2] + "0" + old[2:]
        return file_name.replace(old, new)

    @classmethod
    def __add_task_id(cls, file_name):
        data_name = file_name.split("_")[0]
        data_info = cls.data_info[cls.data_info["name"] == data_name]
        if len(data_info) == 0:
            print(file_name)
            raise Exception(f"데이터 이름({data_name})가 master table에 없습니다.")
        if len(data_info) > 1:
            print(file_name)
            raise Exception(f"데이터 이름({data_name})가 master table에 여러 개 들어있습니다.")
        number = data_info['number'].tolist()[0]
        code = data_info['code'].tolist()[0]
        file_name = f"[{number}-{code}] {file_name}"
        return file_name


class CorrectWrongId(Correct):
    @classmethod
    def execute(cls, file_name):
        file_name = cls.__except_correct(file_name)
        return file_name

    @classmethod
    def __except_correct(cls, file_name):
        """ 예외 케이스 처리 """
        except_dict = {
            "2-019-294": "3-019-294",
            "2-062-194": "2-063-194"
        }

        for old, new in except_dict.items():
            if old in file_name:
                file_name = file_name.replace(old, new)
        return file_name


class AddTaskCode(Correct):
    """
    x-xxx-xxx -> x-xxx-xxx-AZ
    """
    CODE_PATTERN = "[A-Z]{2}"
    NO_CODE_PATTERN = "\d-\d{3}-\d{3}"

    @classmethod
    def execute(cls, file_name):
        """
        _1-001-001_ 구문정확성사전검사결과...
        - > _1-001-001-CV_ 구문정확성사전검사결과...

        [1-001-001_CV] 구문정확성사전검사결과...
        [1-001-001] 구문정확성사전검사결과...
        - > [1-001-001-CV] 구문정확성사전검사결과...
        """
        validate_pattern = re.compile(cls.CODE_PATTERN)
        if validate_pattern.search(file_name) is not None:
            return file_name
        file_name = cls.__add_code_in_task_id(file_name)
        return file_name

    @classmethod
    def __add_code_in_task_id(cls, file_name):
        error_find_pattern = re.compile(cls.NO_CODE_PATTERN)
        task_id = error_find_pattern.search(file_name)
        if task_id is None:
            return file_name
        start, end = task_id.span()
        old = file_name[start:end]
        try:
            new = cls.__add_code_to_number(old)
        except Exception as e:
            print(file_name)
            raise
        return file_name.replace(old, new)

    @classmethod
    def __add_code_to_number(cls, number):
        """ 1-001-001 -> 1-001-001-CV """
        match_series = cls.data_info[cls.data_info['number'] == number].apply(
            lambda row: row[0]+"-"+row[1], axis=1)
        if len(match_series) == 0:
            raise Exception(f"과제 번호({number})가 master table에 없습니다.")
        if len(match_series) > 1:
            raise Exception(f"과제 번호({number})가 master table에 여러 개 들어있습니다.")
        return match_series.tolist()[0]


class CorrectTaskId(Correct):
    """
    x-xxx-xxx_AZ -> x-xxx-xxx-AZ
    """
    AVAILABLE_PATTERN = "\d-\d{3}-\d{3}-[A-Z]{2}"

    @classmethod
    def execute(cls, file_name):
        """
        [1-001-001_CV] 구문정확성사전검사결과... - > [1-001-001-CV] 구문정확성사전검사결과...
        [1-001-001] 구문정확성사전검사결과... - > [1-001-001-CV] 구문정확성사전검사결과...
        """
        validate_pattern = re.compile(cls.AVAILABLE_PATTERN)
        if validate_pattern.search(file_name) is not None:
            return file_name

        file_name = cls.__correct_underscore_in_task_id(file_name)
        file_name = cls.__correct_space_in_task_id(file_name)
        return file_name

    @classmethod
    def __correct_underscore_in_task_id(cls, file_name):
        format = "\d-\d{3}-\d{3}_[A-Z]{2}"
        underscore_find_pattern = re.compile(format)
        error = underscore_find_pattern.search(file_name)
        if error is None:
            return file_name
        start, end = error.span()
        old = file_name[start:end]
        new = old.replace("_", "-")
        return file_name.replace(old, new)

    @classmethod
    def __correct_space_in_task_id(cls, file_name):
        format = "\d-\d{3}-\d{3} [A-Z]{2}"
        underscore_find_pattern = re.compile(format)
        error = underscore_find_pattern.search(file_name)
        if error is None:
            return file_name
        start, end = error.span()
        old = file_name[start:end]
        new = old.replace(" ", "-")
        return file_name.replace(old, new)


class CorrectBracket(Correct):
    """
    x-xxx-xxx 통계...
    x-xxx-xxx통계...
    (x-xxx-xxx) 통계...
    _x-xxx-xxx_ 통계...
    x-xxx-xxx_ 통계...

    -> x-xxx-xxx
    """
    AVAILABLE_PATTERN = "\[\d-\d{3}-\d{3}-[A-Z]{2}\] "

    @classmethod
    def execute(cls, file_name):
        validate_pattern = re.compile(cls.AVAILABLE_PATTERN)
        if validate_pattern.search(file_name) is not None:
            return file_name

        start, end = cls.__extract_task_id_range(file_name)
        # left bracket
        if start == 0:
            file_name = "[" + file_name
            end += 1
        elif start == 1:
            file_name = "[" + file_name[1:]
        else:  # start > 2:
            raise Exception(f"task_id 두번째 글자부터 시작합니다. {file_name}")

        # right bracket
        if file_name[end:end+2] == ")_":
            file_name = file_name[:end] + "]" + file_name[end+2:]
        elif file_name[end:end+2] == "]_":  # "_" : end+1
            print(file_name)
            file_name = file_name[:end+1] + file_name[end+2:]
        elif file_name[end] in ["_", ")"]:
            file_name = file_name[:end] + "]" + file_name[end+1:]
        elif file_name[end] == " ":
            file_name = file_name[:end] + "]" + file_name[end:]
        elif file_name[end] == "]":
            pass
        else:  # file_name[end+1]에서 띄어쓰기 없이 바로 가는 경우
            file_name = file_name[:end] + "]" + file_name[end:]
        return file_name

    @classmethod
    def __extract_task_id_range(cls, file_name):
        format = "\d{1}-\d{3}-\d{3}-[A-Z]{2}"
        finder = re.compile(format)
        task_id = finder.search(file_name)
        if task_id is None:
            raise Exception(f"{file_name} 에 유효한 과제 아이디가 없습니다.")
        return task_id.span()

    # @classmethod
    # def _correct_underscore(cls, file_name):
    #     format = "\_\d{1}-\d{3}-\d{3}-[A-Z]{2}\_"
    #     finder = re.compile(format)
    #     s, e = finder.search(file_name).span()
    #     target = file_name[s:e]
    #     file_name.replace(target, "[" + target[1:9])
    #     pass

    # @classmethod
    # def _correct_parentheses(cls, file_name):
    #     format = "\(\d{1}-\d{3}-\d{3}-[A-Z]{2}\)"
    #     pass

#########################################################
#########################################################
#########################################################
#########################################################


class CorrectDuplication(Correct):
    @classmethod
    def execute(cls, file_name):
        finder = re.compile(f"\(\d\)\.{cfg.EXTENSION_FORMAT}")
        find = finder.search(file_name)
        if find is None:
            return file_name

        s = find.start()
        file_name = file_name[:s] + file_name[s+3:]
        return file_name


class CorrectDate(Correct):
    """ [year(start, end), month(start, end), day(start, end)] """
    date_dict = {
        "22\d{4}": [(0, 2), (2, 4), (4, 6)],
        "2022\d{4}": [(2, 4), (4, 6), (6, 8)],
        "2022-\d{2}-\d{2}": [(2, 4), (5, 7), (8, 10)],
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
    def execute(cls, file_name):
        """
        yyyy-mm-dd -> yymmdd
        ^*hh mm ss$ -> ^*yymmdd$
        """
        # date formatting
        file_name = cls.__edit_date_format(file_name)

        # remove hh mm ss
        for time_format in cls.time_list:
            time = cls.__find_date(file_name, time_format)
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
            date = cls.__find_date(input, date_format)  # None or Date
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
        date = cls.__find_date(file_name, "22\d{4}")
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
    def __find_date(cls, date_part, date_format):
        date_finder = re.compile(date_format)
        date = date_finder.search(date_part)
        if date is None:
            return None
        start, end = date.span()
        return date_part[start: end]

    @ classmethod
    def __validate_date_format(cls, date):
        date_finder = re.compile(cfg.DATE_FORMAT)
        if date_finder.match(date) is None:
            raise Exception("날짜 형식이 완벽하게 수정되지 않았습니다.")


class CorrectResultType(Correct):
    rename_dict = {
        '구문정확성사전검사결괴': '구문정확성사전검사결과',
        '구문정확성서전검사결과': '구문정확성사전검사결과',
        '구문정확성검사': '구문정확성사전검사결과',
        '통계다양성검사': '통계다양성사전검사결과',
        '오류로그목록': '사전검사형식오류목록',

        '구문정확성사전검사결과_구조오류목록': '사전검사구조오류목록',
        '구문정확성사전검사결과_형식오류목록': '사전검사형식오류목록',
        '구문정확성사전검사결과_파일오류목록': '사전검사파일오류목록',
        # '사전검사사전검사': ""
    }

    reg_dict = {
        '((?<!사전검사)형식오류목록)': '사전검사형식오류목록',
        '((?<!사전검사)파일오류목록)': '사전검사파일오류목록',
        '((?<!사전검사)구조오류목록)': '사전검사구조오류목록',
    }

    # rename_dict1 = {
    #     '구문정확성검사': '구문정확성사전검사결과',
    #     '통계다양성검사': '통계다양성사전검사결과',

    #     ']형식오류목록': '] 사전검사형식오류목록',
    #     ' 형식오류목록': ' 사전검사형식오류목록',
    #     ']구조오류목록': '] 사전검사구조오류목록',
    #     ' 구조오류목록': ' 사전검사구조오류목록',
    #     ']파일오류목록': '] 사전검사파일오류목록',
    #     ' 파일오류목록': ' 사전검사파일오류목록',

    #     ']사전검사형식오류목록': '] 사전검사형식오류목록',
    #     ' 사전검사형식오류목록': ' 사전검사형식오류목록',
    #     ']사전검사구조오류목록': '] 사전검사구조오류목록',
    #     ' 사전검사구조오류목록': ' 사전검사구조오류목록',
    #     ']사전검사파일오류목록': '] 사전검사파일오류목록',
    #     ' 사전검사파일오류목록': ' 사전검사파일오류목록',
    # }

    # rename_dict2 = {
    #     ']구문정확성사전검사결과': '] 구문정확성사전검사결과',
    #     ']통계다양성사전검사결과': '] 통계다양성사전검사결과',
    # }

    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__apply_rename_dict(file_name)
        file_name = cls.__apply_reg_dict(file_name)
        return file_name

    @ classmethod
    def __apply_rename_dict(cls, file_name):
        for error, right in cls.rename_dict.items():
            file_name = file_name.replace(error, right)
        return file_name

    @ classmethod
    def __apply_reg_dict(cls, file_name):
        for format, edit in cls.reg_dict.items():
            finder = re.compile(format)
            error = finder.search(file_name)
            if error is None:
                continue
            s, e = error.span()
            error_text = file_name[s: e]
            file_name = file_name.replace(error_text, edit)
        return file_name


class CorrectSequence(Correct):
    """
    [1-014-044-NL] 페르소나 대화 데이터_사전검사형식오류목록_220825.csv
    -> [1-014-044-NL] 사전검사형식오류목록_페르소나 대화 데이터_220825.csv

    """
    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__change_result_type_order(file_name)
        return file_name

    @ classmethod
    def __change_result_type_order(cls, file_name):
        result_types = [
            '구문정확성사전검사결과',
            '통계다양성사전검사결과',
            '사전검사형식오류목록',
            '사전검사파일오류목록',
            '사전검사구조오류목록',
        ]

        splitted = file_name.split("_")
        if splitted[1] not in result_types:
            return file_name
        task_id_name = splitted[0].split("] ")
        task_id = task_id_name[0] + "]"
        task_name = task_id_name[1]
        result_type = splitted[1]
        date_extension = splitted[2]

        file_name = f"{task_id} {result_type}_{task_name}_{date_extension}"
        return file_name


class CorrectSpace(Correct):

    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__correct_zero_space(file_name)
        file_name = cls.__correct_many_space(file_name)
        file_name = cls.__correct_space_dot(file_name)
        return file_name

    @ classmethod
    def __correct_zero_space(cls, file_name):
        format = "\](구문|통계|사전)"
        finder = re.compile(format)
        error = finder.search(file_name)
        if error is None:
            return file_name

        s, e = error.span()
        error_text = file_name[s: e]
        edit = error_text[: 1] + " " + error_text[1:]
        return file_name.replace(error_text, edit)

    @ classmethod
    def __correct_many_space(cls, file_name):
        format = "\s{2,}"
        finder = re.compile(format)
        while True:
            error = finder.search(file_name)
            if error is None:
                break
            file_name = file_name.replace("  ", " ")
        return file_name

    @ classmethod
    def __correct_space_dot(cls, file_name):
        """ "yymmdd .xlsx" - > "yymmdd.xlsx" """
        finder = re.compile(f"\.{cfg.EXTENSION_FORMAT}")
        find = finder.search(file_name)
        if find is None:
            return file_name

        s = find.start()
        if file_name[s-1] == " ":
            file_name = file_name[:s-1] + file_name[s:]
        return file_name


class CorrectDelimiter(Correct):
    """
    결과서 타입이 명확해야 하기 때문에 CorrectResultType 이후에 동작해야 함.
    """

    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__around_result_type(file_name)
        return file_name

    @classmethod
    def __around_result_type(cls, file_name):
        """
        [2-060-190-MA] 통계다양성사전검사결과 2차_3D프린팅 출력물 형상 보정용 데이터 (수축분석)_221115.xlsx
        -> [2-060-190-MA] 통계다양성사전검사결과_2차_3D프린팅 출력물 형상 보정용 데이터 (수축분석)_221115.xlsx
        """
        # if file_name == "[2-060-190-MA] 통계다양성사전검사결과 2차_3D프린팅 출력물 형상 보정용 데이터 (수축분석)_221115.xlsx":
        #     import pdb
        #     pdb.set_trace()
        finder = re.compile(cfg.RESULT_TYPE_FORMAT)
        find = finder.search(file_name)

        if find is None:
            raise Exception(
                f"{file_name} 에 유효한 문서 타입이 없습니다. CorrectResultType을 점검해주세요.")

        e = find.end()
        if file_name[e] == " ":
            file_name = file_name[:e] + "_" + file_name[e+1:]
            return file_name

        finder = re.compile("[가-힣a-zA-Z0-9]")
        find = finder.match(file_name[e])
        if find is None:
            return file_name
        file_name = file_name[:e] + "_" + file_name[e:]
        return file_name


class CorrectRepeatExtension(Correct):
    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__remove_duplicated_extension(file_name)
        return file_name

    @classmethod
    def __remove_duplicated_extension(cls, file_name):
        # if file_name == "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020.csv.csv":
        #     import pdb
        #     pdb.set_trace()
        finder = re.compile(f"\.{cfg.EXTENSION_FORMAT}")

        find_list = []
        for find in finder.finditer(file_name):
            find_list.append(find)

        # 마지막 빼고 모두 제거
        if len(find_list) > 1:
            for find in find_list[:-1]:
                file_name = file_name.replace(find.group(), "", 1)

        return file_name


class CorrectBody(Correct):
    validate_pattern = [
        cfg.ID_FORMAT,
        cfg.CATEGORY_FORMAT,
        cfg.RESULT_TYPE_FORMAT,
        cfg.DATE_FORMAT,
        cfg.EXTENSION_FORMAT
    ]

    @ classmethod
    def execute(cls, file_name):
        old_body = cls.__extract_body(file_name)
        new_body = cls.__clean_duplicates(old_body)
        if old_body != new_body:
            file_name = file_name.replace(old_body, new_body)
        return file_name

    @classmethod
    def __extract_body(cls, file_name):
        s = cls.__get_start_index_of_body(file_name)
        e = cls.__get_end_index_of_body(file_name)
        return file_name[s:e]

    @classmethod
    def __get_start_index_of_body(cls, file_name):
        """
        "^\[{ID_FORMAT}-{CATEGORY_FORMAT}\] {RESULT_TYPE_FORMAT}_{BODY_FORMAT}_{DATE_FORMAT}\.{EXTENSION_FORMAT}$"
        에서 RESULT_TYPE_FOMRAT 바로 뒤부터
        """

        finder = re.compile(cfg.RESULT_TYPE_FORMAT)
        find = finder.search(file_name)
        if find is None:
            raise ValueError(
                f"{file_name} 에 유효한 문서 타입이 없습니다. CorrectResultType을 점검해주세요.")
        return find.end()

    @ classmethod
    def __get_end_index_of_body(cls, file_name):
        finder = re.compile(cfg.DATE_FORMAT)
        find = finder.search(file_name)
        if find is None:
            raise ValueError(
                f"{file_name} 에 유효한 날짜 형식이 없습니다. CorrectDate를 점검해주세요.")
        return find.start()

    @ classmethod
    def __clean_duplicates(cls, body):
        for pattern in cls.validate_pattern:
            if cls.__is_valid_body(body, pattern):
                continue
            body = cls.__remove_pattern_in_body(body, pattern)
        return body

    @ classmethod
    def __is_valid_body(cls, body, pattern):
        validator = re.compile(pattern)
        return validator.search(body) is None

    @ classmethod
    def __remove_pattern_in_body(cls, body, pattern):
        error = cls.__find(body, pattern)
        if error is None:
            return body
        return body.replace(error, "")

    @ classmethod
    def __find(cls, text, pattern):
        finder = re.compile(pattern)
        find = finder.search(text)
        if find is None:
            return None
        return find.group()

        # Test
if __name__ == "__main__":
    root = "C:/Users/seohy/workspace/upload_S3/test-data/사전검사결과"
    file_list = [
        # 날짜 형식 테스트
        "[1-001-002-CV] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27 09 11 42.xlsx",
        "[1-001-002-CV] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        "[1-001-002-CV]구문정확성사전검사결과_비디오 전환 경계 추론 데이터_220927.xlsx",

        "[1-001-002]구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",
        "[1-001-002] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",
        "[1-001-002]_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",

        "1-001-002구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "1-001-002_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "1-001-002구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        "_1-001-002_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "_1-001-002_ 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        "(1-001-002)구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "(1-001-002)_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "(1-001-002) 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        "(1-001-002)  형식오류목록_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "(1-001-002)  사전검사형식오류목록_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "페르소나 대화 데이터_형식오류목록_2022-08-25 14_07_54.csv",

        "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020.csv.csv",

        "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020 (1).csv",

        "[2-095-236-EN] 형식오류목록_지하수 수량·수질 데이터 (이용량)_형식오류목록_221020.csv",
    ]
    file_list = [path_join(root, file) for file in file_list]
    correct = Correct(file_list)
    correct.execute(p=True)
    # correct.copy_to(cfg.RESULT_DIR_EDIT)

    # correct.rename(cfg.RESULT_DIR_EDIT)
    # correct.rename(new_root)
