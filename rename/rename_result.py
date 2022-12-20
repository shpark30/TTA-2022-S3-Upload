import pandas as pd

import sys
from pathlib import Path
root = Path(__file__).parent.parent
sys.path.append(str(root))

import local_config as cfg
from utils import path_join, find_files_in_dir

from rename.correct import Correct
from rename.correct.correct_id import (CorrectIdDigits, AddTaskId, CorrectIdMaually,
                                     AddTaskCode, CorrectIdBracket)
from rename.correct.correct_type import CorrectResultType, CorrectTypeDelimiter
from rename.correct.correct_body import CorrectBody
from rename.correct.correct_date import CorrectDate
from rename.correct.correct_etc import (CorrectDuplication, CorrectSequence,
                                      CorrectSpace, CorrectRepeatExtension, CorrectDunder)

# 메타클래스 정의(클래스를 생성하는 클래스)


def result_corrector(file_list):
    correct_sub_classes = [
        CorrectDuplication,
        CorrectRepeatExtension,

        # correct id
        CorrectIdDigits,
        AddTaskId,
        CorrectIdMaually,
        # CorrectTaskId,
        # CorrectIdDelimiter,
        AddTaskCode,

        CorrectIdBracket,

        # correct date
        CorrectDate,

        # correct type
        CorrectResultType,
        CorrectTypeDelimiter,

        # correct body
        CorrectBody,

        # correct Sequence
        CorrectSpace,
        CorrectSequence,

        CorrectDunder,  # CorrectBody에서 __ 생길 수 있어서 마지막에 해야 함
    ]

    correct = Correct(file_list)
    for sub_class in correct_sub_classes:
        correct.register(sub_class)
    return correct

def rename_result(ver, date):
    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.RESULT_DIR_ORIGINAL.format(ver, date), pattern="^((?!증적용).)*\.(csv|xlsx)$")

    # data info
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding='cp949')

    # 파일명 수정 및 New directory로 이동
    correct = result_corrector(file_list)
    correct.execute(data_info)
    correct.remove_older_files(p=True)
    correct.copy_to(cfg.RESULT_DIR_EDIT.format(ver, date))


# Test
if __name__ == "__main__":
    root = "C:/Users/seohy/workspace/upload_S3/test-data/사전검사결과"
    file_list = [
        # 날짜 형식 테스트
        "[1-001-002-CV] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27 09 11 42.xlsx",
        "[1-001-002-CV] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        # 코드
        "[1-001-002] 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",

        # 띄어쓰기 없을 때
        "[1-001-002]구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",
        "[1-001-002-CV]구문정확성사전검사결과_비디오 전환 경계 추론 데이터_220927.xlsx",
        "[1-001-002]_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_20220927.xlsx",

        # 대괄호 없을 때
        "1-001-002구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "1-001-002_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        # 대괄호 대신 언더바가 쓰였을 때
        "_1-001-002_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "_1-001-002_ 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",

        # 대괄호 대신 소괄호가 쓰였을 때
        "(1-001-002)구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "(1-001-002)_구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "(1-001-002) 구문정확성사전검사결과_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",


        # 띄어쓰기 두번 쓰였을 때
        "(1-001-002)  형식오류목록_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",
        "(1-001-002)  사전검사형식오류목록_비디오 전환 경계 추론 데이터_2022-09-27.xlsx",


        # 과제 아이디 없을 때 & 형식오류목록 순서 & 시간까지 쓰였을 때
        "페르소나 대화 데이터_형식오류목록_2022-08-25 14_07_54.csv",

        # 확장자가 파일명에 들었을 때
        "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020.csv.csv",

        # (숫자) 복사본일 때
        "[2-095-236-EN] 사전검사형식오류목록_지하수 수량·수질 데이터 (이용량)_221020 (1).csv",

        # 동일한 문서가 날짜 버전만 다를 때
        "[2-095-236-EN] 형식오류목록_지하수 수량·수질 데이터 (이용량)_형식오류목록_221020.csv",
        "[2-095-236-EN] 형식오류목록_지하수 수량·수질 데이터 (이용량)_형식오류목록_220910.csv",

        "[1-047-119-SA] 통계다양성사전검사결과_IR 실제 환경 안면 검출 및 인식 데이터 (wider)_221005.xlsx",

        "[2-095-235-EN] 사전검사형식오류목록_상수원·취수원 통합 수질 및 녹조 데이터(상수원·취수원 수질데이터_geojson)_20221110.xlsx",

    ]
    file_list = [path_join(root, file) for file in file_list]
    file_list = find_files_in_dir("W:/2022 TTA/2022 이관/사전/검사 결과/12.12", pattern="^((?!증적용).)*\.(csv|xlsx)$")
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format("사전"), encoding="cp949")
    correct = result_corrector(file_list)

    old_files_len = len(correct)
    import pdb
    pdb.set_trace()
    rename_result("사전", "12.12")
    correct.execute(data_info, p=True)
    before_remove_len = len(correct)

    correct.remove_older_files(p=True)

    after_remove_len = len(correct)
    print(old_files_len, before_remove_len, after_remove_len)

    # # rename
    # correct = Correct([])
    # correct.rename(cfg.RESULT_DIR_EDIT, p=True)
    # correct.rename(new_root)
