from utils import path_join

from rename.correct.correct import Correct
from rename.correct.correct_id import (AddTaskId, CorrectIdMaually,
                                       AddTaskCode, CorrectTaskId, CorrectIdBracket)
from rename.correct.correct_type import CorrectResultType, CorrectDelimiter
from rename.correct.correct_body import CorrectBody
from rename.correct.correct_date import CorrectDate
from rename.correct.correct_etc import (CorrectDuplication, CorrectSequence,
                                        CorrectSpace, CorrectRepeatExtension, CorrectDunder)

# 메타클래스 정의(클래스를 생성하는 클래스)

correct_sub_classes = [
    CorrectSpace,
    CorrectDuplication,
    CorrectDunder,

    # correct id
    AddTaskId,
    CorrectIdMaually,
    AddTaskCode,
    CorrectTaskId,
    CorrectIdBracket,

    # correct type
    CorrectResultType,
    CorrectDelimiter,

    # correct body
    CorrectBody,

    # correct date
    CorrectDate,

    # correct Sequence
    CorrectSequence,
]

for sub_class in correct_sub_classes:
    Correct.register(sub_class)

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


# Test
if __name__ == "__main__":
    root = "C:/Users/seohy/workspace/upload_S3/test-data/사전검사결과"
    file_list = [
        # # 날짜 형식 테스트
        # "[1-001-002-CV] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27 09 11 42.xlsx",
        # "[1-001-002-CV] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        # # 코드
        # "[1-001-002] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",

        # # 띄어쓰기 없을 때
        # "[1-001-002]구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",
        # "[1-001-002-CV]구문정확성사전검사결과_비디오 전환 경계 추론 데이터_220927.xlsx",
        # "[1-001-002]_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",

        # # 대괄호 없을 때
        # "1-001-002구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        # "1-001-002_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        # # 대괄호 대신 언더바가 쓰였을 때
        # "_1-001-002_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        # "_1-001-002_ 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        # # 대괄호 대신 소괄호가 쓰였을 때
        # "(1-001-002)구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        # "(1-001-002)_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        # "(1-001-002) 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",


        # # 띄어쓰기 두번 쓰였을 때
        # "(1-001-002)  형식오류목록_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        # "(1-001-002)  사전검사형식오류목록_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",


        # # 과제 아이디 없을 때 & 형식오류목록 순서 & 시간까지 쓰였을 때
        # "페르소나 대화 데이터_형식오류목록_2022-08-25 14_07_54.csv",

        # # 확장자가 파일명에 들었을 때
        # "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020.csv.csv",

        # # (숫자) 복사본일 때
        # "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020 (1).csv",

        # # 동일한 문서가 날짜 버전만 다를 때
        # "[2-095-236-EN] 형식오류목록_지하수 수량·수질 데이터 (이용량)_형식오류목록_221020.csv",
        # "[2-095-236-EN] 형식오류목록_지하수 수량·수질 데이터 (이용량)_형식오류목록_220910.csv",

        "[1-047-119-SA] 통계다양성사전검사결과_IR 실제 환경 안면 검출 및 인식 데이터 (wider)_221005.xlsx",
    ]
    file_list = [path_join(root, file) for file in file_list]
    correct = Correct(file_list)

    old_files_len = len(correct)
    correct.execute(p=True)
    before_remove_len = len(correct)

    correct.remove_older_files(p=True)

    after_remove_len = len(correct)
    print(old_files_len, before_remove_len, after_remove_len)

    # # rename
    # correct = Correct([])
    # correct.rename(cfg.RESULT_DIR_EDIT, p=True)
    # correct.rename(new_root)
