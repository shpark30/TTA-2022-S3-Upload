import unittest
import pandas as pd
from copy import deepcopy

import local_config as cfg
from utils import find_files_in_dir
from core.rename_checklist import correct_register


class ValidateBeforeChecklistTest(unittest.TestCase):
    ver = "사전"
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding="cp949")
    date = data_info.columns[-1]
    files = find_files_in_dir(cfg.REPORT_DIR_EDIT.format(
        ver, date), pattern="^.*\.docx$")
    assert len(files) > 0

    def test_정상(self):
        corrector = correct_register(self.files)
        corrector.execute(self.data_info)
        corrector.remove_older_files(p=True)
        corrector
        
    def test_최신_날짜가_아닌_경우(self):
        corrector = correct_register(self.files)
        corrector.execute(self.data_info)
        corrector.remove_older_files(p=True)
        self.assertRaises(
            AssertionError, corrector.validate_before, "11.23")

    def test_data_info에_없는_날짜인_경우(self):
        corrector = correct_register(self.files)
        corrector.execute(self.data_info)
        corrector.remove_older_files(p=True)
        self.assertRaises(AssertionError, corrector.validate_before, "12.03")

    def test_data_info상_직전_이관_대상이_이번_이관_대상에_없는_경우(self):
        corrector = correct_register(self.files)
        data_info = deepcopy(self.data_info)
        idx = data_info[data_info.iloc[:, -1] != "확인 완료"].index[0]
        data_info.iloc[idx, -2] = "확인 완료"
        corrector.execute(data_info)
        corrector.remove_older_files(p=True)
        self.assertRaises(
            AssertionError, corrector.validate_before, self.date)

    def test_새로_이관할_파일과_data_info상_확인_완료된_파일이_다른_경우(self):
        corrector = correct_register(self.files+[f"[3-035-310-UT] {self.ver}이슈리포트_AI기반 국립공원 변화탐지 모니터링 플랫폼 구축_221025.docx"])
        corrector.execute(self.data_info)
        corrector.remove_older_files(p=True)
        self.assertRaises(AssertionError, corrector.validate_before, self.date)


if __name__ == '__main__':
    unittest.main()
