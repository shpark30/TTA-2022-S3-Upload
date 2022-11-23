from copy import deepcopy
import pandas as pd
from abc import ABC, abstractmethod
import shutil
from tqdm import tqdm
import re
import os

from utils import path_join, extract_task_id
import local_config as cfg

# 메타클래스 정의(클래스를 생성하는 클래스)


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
            new_cls.REGISTRY = {}
        return new_cls


class Correct(metaclass=RegistryMetaClass):
    def __init__(self, file_list: list):
        self.old_file_list = file_list
        self.new_file_list = {}

    def execute(self, p=True):
        if len(self.new_file_list):
            print("이미 execute를 실행했습니다.")
            return

        for file_path in self.old_file_list:
            file_name = file_path.split("/")[-1]
            self.new_file_list[file_path] = self._correct(file_name, p=p)

    def copy_to(self, root, progress_bar: bool = True):
        """ 기존 파일의 수정 버전을 root 하위에 옮긴다. """
        if len(self.new_file_list) == 0:
            print("new_file_list가 비어있습니다. execute 메서드를 먼저 실행해주시기 바랍니다.")
            return

        if not os.path.exists(root):
            print(f"{root} 경로가 존재하지 않습니다.")
            return

        exit = False
        for old_path, new_name in self.new_file_list.items():
            if "/" in new_name:
                print("새로운 파일 이름에 경로 구분자(/, \\)가 들어있습니다.")
                print("기존: " + old_path)
                print("수정: " + new_name)
                print("")
                exit = True
        if exit:
            return

        if progress_bar:
            bar = tqdm(self.new_file_list.items(),
                       total=len(self.new_file_list))
        else:
            bar = self.new_file_list.items()

        for old_path, new_name in bar:
            new_path = path_join(root, new_name)
            if not os.path.exists(new_name):
                shutil.copy(old_path, new_path)

    def _correct(self, file_path: str, p=True) -> str:
        file_name = file_path.split("\\")[-1]
        prev_name = deepcopy(file_name)
        for name, sub_class in self.REGISTRY.items():
            file_name = sub_class.execute(file_name)
        if p and prev_name != file_name:
            print("기존: " + prev_name)
            print("변경: " + file_name)
            print()
        return file_path.replace(prev_name, file_name)


class CorrectDocType(Correct):
    rename_dict1 = {
        '구문정확성검사': '구문정확성사전검사결과',
        '통계다양성검사': '통계다양성사전검사결과',

        ']형식오류목록': '] 사전검사형식오류목록',
        ' 형식오류목록': ' 사전검사형식오류목록',
        ']구조오류목록': '] 사전검사구조오류목록',
        ' 구조오류목록': ' 사전검사구조오류목록',
        ']파일오류목록': '] 사전검사파일오류목록',
        ' 파일오류목록': ' 사전검사파일오류목록',
    }

    rename_dict2 = {
        ']구문정확성사전검사결과': '] 구문정확성사전검사결과',
        ']통계다양성사전검사결과': '] 통계다양성사전검사결과',
    }

    @classmethod
    def execute(cls, file_name):
        file_name = cls._apply_rename_dict(file_name, cls.rename_dict1)
        file_name = cls._apply_rename_dict(file_name, cls.rename_dict2)
        return file_name

    @classmethod
    def _apply_rename_dict(cls, file_name, dict):
        for error, right in dict.items():
            file_name = file_name.replace(error, right)
        return file_name


class CorrectTaskId(Correct):
    AVAILABLE_PATTERN = "\d-\d{3}-\d{3}-[A-Z]{2}"
    UNDERSCORE_PATTERN = "\d-\d{3}-\d{3}_[A-Z]{2}"
    NO_CODE_PATTERN = "\[\d-\d{3}-\d{3}\]"

    @classmethod
    def execute(cls, file_name):
        """ 
        [1-001-001_CV] 구문정확성사전검사결과... - > [1-001-001-CV] 구문정확성사전검사결과... 
        [1-001-001] 구문정확성사전검사결과... - > [1-001-001-CV] 구문정확성사전검사결과... 
        """
        validate_pattern = re.compile(cls.AVAILABLE_PATTERN)
        if validate_pattern.search(file_name) is not None:
            return file_name
        file_name = cls._except_correct(file_name)
        file_name = cls._correct_underscore_in_task_id(file_name)
        file_name = cls._add_code_in_task_id(file_name)
        return file_name

    @classmethod
    def _except_correct(cls, file_name):
        """ 예외 케이스 처리 """
        except_dict = {
            "2-019-294": "3-019-294"
        }

        for old, new in except_dict.items():
            if old in file_name:
                file_name = file_name.replace(old, new)
        return file_name

    @classmethod
    def _correct_underscore_in_task_id(cls, file_name):
        underscore_find_pattern = re.compile(cls.UNDERSCORE_PATTERN)
        error = underscore_find_pattern.search(file_name)
        if error is None:
            return file_name
        start, end = error.span()
        old = file_name[start:end]
        new = old.replace("_", "-")
        return file_name.replace(old, new)

    @classmethod
    def _add_code_in_task_id(cls, file_name):
        error_find_pattern = re.compile(cls.NO_CODE_PATTERN)
        error = error_find_pattern.search(file_name)
        if error is None:
            return file_name
        start, end = error.span()
        old = file_name[start+1:end-1]
        try:
            new = cls._add_code_to_number(old)
        except Exception as e:
            print(file_name)
            raise
        return file_name.replace(old, new)

    @classmethod
    def _add_code_to_number(cls, number):
        """ 1-001-001 -> 1-001-001-CV """
        task_table = pd.read_csv(cfg.DATA_INFO_PATH)
        match_series = task_table[task_table['number'] == number].apply(
            lambda row: row[0]+"-"+row[1], axis=1)
        if len(match_series) == 0:
            raise Exception(f"과제 번호({number})가 master table에 없습니다.")
        if len(match_series) > 1:
            raise Exception(f"과제 번호({number})가 master table에 여러 개 들어있습니다.")
        return match_series.tolist()[0]


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

    @classmethod
    def execute(cls, file_name):
        """
        yyyy-mm-dd -> yymmdd
        ^*hh mm ss$ -> ^*yymmdd$
        """
        # date formatting
        file_name = cls._edit_date(file_name)

        # remove hh mm ss
        for time_format in cls.time_list:
            time = cls._find(file_name, time_format)
            if time is None:
                continue
            file_name = file_name.replace(time, "")

        # 날짜가 없으면 추가
        if not cls._is_date_in(file_name):
            file_name = cls._add_date(file_name)

        # validate & #
        date = cls._extract_date_part(file_name)
        try:
            cls._validate_dateformat(date)
        except Exception as e:
            print(file_name)
            raise e
        return file_name

    @classmethod
    def _edit_date(cls, input):
        for date_format, indices in cls.date_dict.items():
            date = cls._find(input, date_format)  # None or Date
            if date is None:
                continue
            new_date = "".join([cls.slicing(date, i) for i in indices])
            input = input.replace(date, new_date)
        return input

    @classmethod
    def _is_date_in(cls, file_name: str) -> bool:
        check_every_format = []
        for date_format in cls.date_dict.keys():
            finder = re.compile(date_format)
            date = finder.search(file_name)
            check_every_format.append(date is not None)
        return any(check_every_format)

    @classmethod
    def _add_date(cls, file_name):
        """ 파일명에 날짜 추가 """
        task_id = extract_task_id(file_name)
        data_info = pd.read_csv(cfg.DATA_INFO_PATH, encoding="cp949")
        complete_date = data_info[data_info["number"]
                                  == task_id]["complete_date"]
        if len(complete_date) == 0:
            raise Exception(f"과제 번호({number})가 master table에 없습니다.")
        if len(complete_date) > 1:
            raise Exception(f"과제 번호({number})가 master table에 여러 개 들어있습니다.")
        complete_date = cls._edit_date(complete_date.tolist()[0])
        delimiter = "."
        splitted = file_name.split(delimiter)
        return f"{delimiter.join(splitted[:-1])}_{complete_date}.{splitted[-1]}"

    @classmethod
    def _extract_date_part(cls, file_name):
        return file_name.split("_")[-1].split(".")[0]

    @classmethod
    def slicing(cls, string: str, index_tuple: tuple) -> str:
        return string[index_tuple[0]: index_tuple[1]]

    @classmethod
    def _find(cls, date_part, date_format):
        date_finder = re.compile(date_format)
        date = date_finder.search(date_part)
        if date is None:
            return None
        start, end = date.span()
        return date_part[start:end]

    @classmethod
    def _validate_dateformat(cls, date):
        date_finder = re.compile("\d{6}")
        if date_finder.match(date) is None:
            raise Exception("날짜 형식이 완벽하게 수정되지 않았습니다.")


# Test
if __name__ == "__main__":
    root = "C:/Users/seohy/workspace/upload_S3/test-data/사전검사결과"
    file_list = [
        "[1-001-002] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",
        "[1-001-002] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "[1-001-002] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27 09 11 42.xlsx"
    ]
    file_list = [path_join(root, file) for file in file_list]
    correct = Correct(file_list)
    correct.execute()
    # correct.copy_to(new_root)
