import re

import local_config as cfg
from .correct import CorrectInterface


class CorrectBody(CorrectInterface):
    validate_pattern = [
        cfg.ID_FORMAT,
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
