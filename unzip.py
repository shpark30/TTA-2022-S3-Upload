import os
from zipfile import ZipFile
import re
from tqdm import tqdm

import pandas as pd

import local_config as cfg
from utils import find_files_in_dir

def main(ver, date):
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding="cp949")

    def _is_mmdd(text):
        validator = re.compile("\d{2}\.\d{2}")
        return validator.match(text) is not None

    date_columns = list(filter(_is_mmdd, list(data_info.columns)))

    if len(date_columns) == 0:
        raise Exception("data_info.csv에 날짜 컬럼이 없습니다.")

    if len(date_columns) == 1:
        pass

    if date != date_columns[-1]:
        print(f"{date}는 최신 날짜가 아닙니다.")
        return

    # 디렉토리 생성
    target_dir = cfg.RESULT_DIR_ORIGINAL.format(ver, date)
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    # 직전 과제 목록 가져오기
    prev_date = date_columns[-2]
    zip_name = cfg.RESULT_DIR_ORIGINAL.format(ver, prev_date) + ".zip"
    with ZipFile(zip_name, 'r') as zip_obj:
        immigrated_tasks = [fn.encode('cp437').decode('utf-8') for fn in zip_obj.namelist()]

    # 이번 과제 목록 가져오기
    zip_name = cfg.RESULT_DIR_ORIGINAL.format(ver, date) + ".zip"
    with ZipFile(zip_name, 'r') as zip_obj:
        to_immigrate_tasks = [fn.encode('cp437').decode('utf-8') for fn in zip_obj.namelist()]
    
    # 과제 목록 비교
    additional = []
    if len(set(immigrated_tasks) - set(to_immigrate_tasks))!=0:
        print("이번 결과서 파일에 없는 직전 결과서 파일이 있습니다.")
        print(set(immigrated_tasks) - set(to_immigrate_tasks))
        contn = input("계속 진행하시겠습니까?(Y, N):")
        assert contn in ["Y", "N"]
        if contn == "N":
            return
        additional = list(set(immigrated_tasks) - set(to_immigrate_tasks))
        
    to_unzip_files = list(set(to_immigrate_tasks) - set(immigrated_tasks))
    to_unzip_files.extend(additional)

    # 이관 대상 과제 압축 풀기
    with ZipFile(zip_name, 'r') as zip_obj:
        zip_files = []
        for file in zip_obj.infolist():
            file.filename = file.filename.encode('cp437').decode('utf-8')
            if file.filename not in to_unzip_files:
                continue
            if os.path.exists(os.path.join(target_dir, file.filename)):
                continue
            zip_files.append(file)

        for file_info in tqdm(zip_files, total=len(zip_files)):
            zip_obj.extract(file_info, target_dir)

    # 개별 과제 압축 파일 풀기
    zip_files = find_files_in_dir(target_dir, pattern="^.*\.zip")
    for zip_file in tqdm(zip_files, total=len(zip_files)):
        with ZipFile(zip_file, 'r') as zip_obj:
            files = []
            for file in zip_obj.infolist():
                file.filename = file.filename.encode('cp437').decode('euc-kr')
                if os.path.exists(os.path.join(target_dir, file.filename)):
                    continue
                files.append(file)

            for file_info in files:
                zip_obj.extract(file_info, target_dir)


if __name__=="__main__":
    ver = input("사전/최종: ")
    date = input("날짜: ")
    main(ver, date)