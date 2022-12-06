import pandas as pd

import local_config as cfg
from utils import find_files_in_dir
from core.rename_checklist import correct_register
ver = "사전"
date = "12.06"

files = find_files_in_dir(cfg.REPORT_DIR_ORIGINAL.format(
    ver, date), pattern="^.*\.docs$")

corrector = correct_register(files)
data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding="cp949")
corrector.execute()
corrector.remove_older_files(p=True)
