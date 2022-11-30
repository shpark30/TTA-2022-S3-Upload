import re

import local_config as cfg
from . import CorrectInterface


class CorrectDuplication(CorrectInterface):
    @classmethod
    def execute(cls, file_name):
        finder = re.compile(f"\(\d\)\.{cfg.EXTENSION_FORMAT}")
        find = finder.search(file_name)
        if find is None:
            return file_name

        s = find.start()
        file_name = file_name[:s] + file_name[s+3:]
        return file_name


class CorrectSequence(CorrectInterface):
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


class CorrectSpace(CorrectInterface):

    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__correct_zero_space(file_name)
        file_name = cls.__correct_many_space(file_name)
        file_name = cls.__correct_space_dot(file_name)
        return file_name

    @ classmethod
    def __correct_zero_space(cls, file_name):
        format = f"^\[{cfg.ID_FORMAT}-{cfg.CATEGORY_FORMAT}\]\S"
        finder = re.compile(format)
        error = finder.search(file_name)
        if error is None:
            return file_name

        error_text = error.group()
        edit = error_text[:-1] + " " + error_text[-1:]
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


class CorrectRepeatExtension(CorrectInterface):
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


class CorrectDunder(CorrectInterface):
    @ classmethod
    def execute(cls, file_name):
        return file_name.replace("__", "_")
