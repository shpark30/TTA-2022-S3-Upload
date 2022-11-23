import os
import pandas as pd
import boto3

import local_config as cfg
from rename import Correct
from utils import path_join, create_folder, find_files_in_dir
from upload import AwsS3Uploader


def create_base_dir_per_task(
        root="C:/Users/seohy/workspace/upload_S3/test-data/테스트디렉토리/과제별/"):
    data_info = pd.read_csv(cfg.DATA_INFO_PATH, encoding='euc-kr')
    data_info["directory"] = data_info.apply(
        lambda row: root + row[0] + "_" + row[2], axis=1)
    folder_names = data_info["directory"].tolist()

    for folder_name in folder_names:
        create_folder(path_join(folder_name, "사전", "검사 규칙"))
        create_folder(path_join(folder_name, "사전", "검사 규칙"))
        create_folder(path_join(folder_name, "최종", "검사 결과서"))
        create_folder(path_join(folder_name, "최종", "검사 결과서"))


def create_base_dir_per_result(
        root="C:/Users/seohy/workspace/upload_S3/test-data/테스트디렉토리/취합본/"):
    for folder in [
            "1.사전검사결과서",
            "2.최종검사결과서",
            "3.사전검사규칙",
            "4.최종검사규칙",
            "5.체크리스트(사전)",
            "6.체크리스트(최종)",
            "7.종료보고서"
            "8.기타"]:
        create_folder(path_join(root, folder))

    for folder in [
            "1.자료미보유확인서",
            "2.구축사업미참여확인서",
            "3.보안서약서 등"
            "4.제3자검증"]:
        create_folder(path_join(root, "8.기타", folder))

    for folder in [
            "1.사전검사결과서",
            "2.최종검사결과서",
            "3.사전검사규칙",
            "4.최종검사규칙",
            "5.체크리스트(사전)",
            "6.체크리스트(최종)",
            "7.종료보고서"]:
        create_folder(path_join(root, "8.기타", "4.제3자검증", folder))


def main(
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    Prefix
):
    # 업로드할 파일 저장소 생성
    create_base_dir_per_task()
    create_base_dir_per_result()

    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.RESULT_DIR_ORIGINAL, pattern="\d-\d{3}-\d{3}")

    # 파일명 수정 및 New directory로 이동
    correct = Correct(file_list)
    correct.execute()
    correct.copy_to(cfg.RESULT_DIR_EDIT)

    # S3 업로드
    uploader = AwsS3Uploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_bucket=aws_bucket,
        Prefix=Prefix
    )

    uploader.upload(find_files_in_dir(cfg.RESULT_DIR_EDIT))


if __name__ == "__main__":
    import access_info as info
    main(aws_access_key_id=info.TEST_ACCESS_KEY_ID,
         aws_secret_access_key=info.TEST_SECRET_ACCESS_KEY,
         aws_bucket=info.TEST_BUCKET_NAME,
         Prefix=info.TEST_ROOT)
