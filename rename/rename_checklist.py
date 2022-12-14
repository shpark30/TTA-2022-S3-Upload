import pandas as pd
import sys
from pathlib import Path

root = Path(__file__).parent.parent
sys.path.append(str(root))

from rename.correct.correct_etc import (CorrectDuplication, CorrectSequence,
                                      CorrectSpace, CorrectRepeatExtension, CorrectDunder)
from rename.correct.correct_date import CorrectDate
from rename.correct.correct_body import CorrectBody
from rename.correct.correct_type import CorrectReportType, AddReportType, CorrectTypeDelimiter
from rename.correct.correct_id import (CorrectIdDigits, AddTaskId, CorrectIdMaually,
                                     AddTaskCode, CorrectIdDelimiter, CorrectIdBracket)
from rename.correct import Correct
import local_config as cfg
from utils import find_files_in_dir


# 메타클래스 정의(클래스를 생성하는 클래스)
def checklist_corrector(file_list):
    correct_sub_classes = [
        CorrectDuplication,
        CorrectRepeatExtension,

        # correct id
        CorrectIdDigits,
        AddTaskId,
        # CorrectTaskId,
        CorrectIdMaually,
        CorrectIdDelimiter,
        AddTaskCode,
        CorrectIdBracket,

        # correct date
        CorrectDate,

        # correct type
        CorrectReportType,
        AddReportType,
        CorrectTypeDelimiter,

        # correct body
        CorrectBody,

        # correct Sequence
        CorrectSpace,
        CorrectSequence,

        CorrectDunder,
    ]

    correct = Correct(file_list)
    for sub_class in correct_sub_classes:
        correct.register(sub_class)
    return correct

def rename_checklist(ver, date):
    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.REPORT_DIR_ORIGINAL.format(ver, date), pattern="^.*\.docx$")

    # data info
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding='cp949')

    # 파일명 수정 및 New directory로 이동
    correct = checklist_corrector(file_list)
    correct.execute(data_info)
    correct.remove_older_files(p=True)
    correct.copy_to(cfg.REPORT_DIR_EDIT.format(ver, date))

# Test
if __name__ == "__main__":
    root = "C:/Users/seohy/workspace/upload_S3/test-data/사전검사결과"
    file_list = [
        # 날짜 형식 테스트
        "[2-047-173-AM] 사전이슈리포트_자율주행 가상센서 시뮬레이션 데이터_2022_11_16.docx",

        # 띄어쓰기
        "[1-036-097-AM] 사전 이슈리포트_상용 자율주행차 악천후 도로 데이터_221019.docx",

        # Type 없음
        "[2-011-132-VO] 연령대별 특징적발화(은어·속성 등) 음성 데이터_221103.docx",
        "_2-061-192_ 사전이슈리포트_바이오의료논문간연계분석데이터_220919.docx",

        # 코드
        "[2-060-190] 사전이슈리포트_3D프린팅 출력물 형상 보정용 데이터_221020.docx",

        #
        "_1-001-002-CV_ 사전 이슈리포트_비디오 전환 경계 추론 데이터_220927.docx",
        "3-011-286-FS_ 사전이슈리포트_이매패류(새조개바지락) 종자생산 데이터_2022_11_14.docx",
    ]
    # file_list = [path_join(root, file) for file in file_list]
    # correct = Correct(file_list)

    # old_files_len = len(correct)
    # correct.execute(p=True)
    # before_remove_len = len(correct)

    # correct.remove_older_files(p=True)

    # after_remove_len = len(correct)
    # print(old_files_len, before_remove_len, after_remove_len)

    # rename
    ver = "사전"
    date = "12.06"

    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.REPORT_DIR_ORIGINAL.format(ver, date), pattern="^.*\.docx$")
    assert len(file_list) > 1
    # 파일명 수정 및 New directory로 이동
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding="cp949")
    correct = correct_register(file_list)
    correct.execute(data_info, p=True)
    correct.remove_older_files(p=True)
    correct.validate_before(date)
    correct.copy_to(cfg.REPORT_DIR_EDIT.format(ver))
