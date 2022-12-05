import os
import re
import pandas as pd

import local_config as cfg
import access_info as info
from rename_result import correct_register
from utils import path_join, find_files_in_dir
from upload import AwsS3Uploader


def main(
    ver,
    date,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    Prefix
):
    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.RESULT_DIR_ORIGINAL.format(ver, date), pattern="^((?!증적용).)*\.(csv|xlsx)$")

    # 파일명 수정 및 New directory로 이동
    correct = correct_register(file_list)
    correct.execute()
    correct.remove_older_files(p=True)
    correct.copy_to(cfg.RESULT_DIR_EDIT.format(ver))

    # S3 업로드
    uploader = AwsS3Uploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_bucket=aws_bucket,
        Prefix=Prefix
    )
    upload_list = find_files_in_dir(cfg.RESULT_DIR_EDIT.format(ver))
    uploader.upload(upload_list, ver)


if __name__ == "__main__":
    # Test 여부
    while 1:
        test = input("테스트 여부를 선택하세요(Y, N): ")
        if test not in ["Y", "N"]:
            print("Y 혹은 N만 입력하세요.")
            continue
        test = test == "Y"
        break

    if test:
        aws_access_key_id = info.ACCESS_KEY_ID,
        aws_secret_access_key = info.SECRET_ACCESS_KEY,
        aws_bucket = info.BUCKET_NAME,
        Prefix = info.ROOT
    else:
        aws_access_key_id = info.TEST_ACCESS_KEY_ID,
        aws_secret_access_key = info.TEST_SECRET_ACCESS_KEY,
        aws_bucket = info.TEST_BUCKET_NAME,
        Prefix = info.TEST_ROOT

    # 사전 / 최종
    while 1:
        ver = input("사전/최종 중 선택하세요: ")
        if ver not in ["사전", "최종"]:
            print("\"사전\" 혹은 \"최종\"만 입력하세요.")
            continue
        break

    # 확인 완료 날짜
    date_validator = re.compile("(11|12|01|02|03)\.(3[0-1]|[0-2][0-9])")
    while 1:
        date = input("날짜를 입력해주세요.(mm.dd): ")
        if date_validator.match(date) is None:
            print("날짜 형식이 올바르지 않습니다.")
            continue
        break

    # 디렉토리 검증
    print("디렉토리 검증 시작")
    for p in [
        cfg.DATA_INFO_PATH.format(ver),
        cfg.RESULT_DIR_ORIGINAL.format(ver, date),
        cfg.RESULT_DIR_EDIT.format(ver),
        cfg.REPORT_DIR_ORIGINAL.format(ver, date),
        cfg.REPORT_DIR_EDIT.format(ver),
        cfg.RULE_DIR_EDIT.format(ver, date),
    ]:
        if not os.path.exists(p):
            raise Exception(f"{p} 경로가 존재하지 않습니다.")
    print("디렉토리 검증 완료")

    # 날짜 검증
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding="cp949")
    if date in data_info.columns:
        print("data_info.csv 날짜 확인 완료")
    else:
        raise Exception(
            f"{cfg.DATA_INFO_PATH.format(ver)}파일에 {date} 컬럼이 없습니다.")

    # # Task 수행
    # main(ver=ver,
    #      date=date,
    #      aws_access_key_id=aws_access_key_id,
    #      aws_secret_access_key=aws_secret_access_key,
    #      aws_bucket=aws_bucket,
    #      Prefix=Prefix)
