from utils import path_join, find_files_in_dir
import local_config as cfg

from rename.correct import Correct
from rename.correct.correct_id import (AddTaskId, CorrectIdMaually,
                                       AddTaskCode, CorrectTaskId, CorrectIdBracket)
from rename.correct.correct_type import CorrectReportType, AddReportType, CorrectTypeDelimiter
from rename.correct.correct_body import CorrectBody
from rename.correct.correct_date import CorrectDate
from rename.correct.correct_etc import (CorrectDuplication, CorrectSequence,
                                        CorrectSpace, CorrectRepeatExtension, CorrectDunder)

# 메타클래스 정의(클래스를 생성하는 클래스)

correct_sub_classes = [
    CorrectDuplication,
    CorrectRepeatExtension,

    # correct id
    AddTaskId,
    CorrectTaskId,
    CorrectIdMaually,
    # CorrectIdDelimiter,
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
    file_list = find_files_in_dir(cfg.REPORT_DIR_ORIGINAL, pattern='docx$')
    import os

    print(len(os.listdir(cfg.REPORT_DIR_ORIGINAL)))
    print(len(file_list))
    correct = Correct(file_list)
    correct.execute(p=True)
    correct.remove_older_files()
    correct.copy_to(cfg.REPORT_DIR_EDIT)
