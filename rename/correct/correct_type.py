import re

import local_config as cfg
from . import CorrectInterface


class CorrectResultType(CorrectInterface):
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


class CorrectReportType(CorrectInterface):
    rename_dict = {
        '] 이슈리포트': '] 사전이슈리포트',
        '사전 이슈리포트': '사전이슈리포트',
        '사전 이슈 리포트': '사전이슈리포트',
    }

    @ classmethod
    def execute(cls, file_name):
        file_name = cls.__apply_rename_dict(file_name)
        return file_name

    @ classmethod
    def __apply_rename_dict(cls, file_name):
        for error, right in cls.rename_dict.items():
            file_name = file_name.replace(error, right)
        return file_name


class AddReportType(CorrectInterface):
    @ classmethod
    def execute(cls, file_name):
        if "사전이슈리포트" in file_name:
            return file_name

        i = file_name.index(" ")+1
        return file_name[:i] + "사전이슈리포트_" + file_name[i:]


class CorrectTypeDelimiter(CorrectInterface):
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
