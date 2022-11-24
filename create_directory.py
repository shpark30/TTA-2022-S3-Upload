import pandas as pd
import local_config as cfg
from utils import path_join, create_folder


def create_base_dir_per_task(
        root="C:/Users/seohy/workspace/upload_S3/test-data/테스트디렉토리/과제별/"):
    data_info = pd.read_csv(cfg.DATA_INFO_PATH, encoding='euc-kr')
    data_info["directory"] = data_info.apply(
        lambda row: root + row[0] + "_" + row[2].replace("/", "·"), axis=1)
    folder_names = data_info["directory"].tolist()

    for folder_name in folder_names:
        create_folder(path_join(folder_name, "사전", "검사 규칙"))
        create_folder(path_join(folder_name, "사전", "검사 결과서"))
        create_folder(path_join(folder_name, "최종", "검사 규칙"))
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
            "7.종료보고서",
            "8.기타"]:
        create_folder(path_join(root, folder))

    for folder in [
            "1.자료미보유확인서",
            "2.구축사업미참여확인서",
            "3.보안서약서 등",
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


if __name__ == "__main__":
    # 업로드할 파일 저장소 생성
    create_base_dir_per_task()
    create_base_dir_per_result()
