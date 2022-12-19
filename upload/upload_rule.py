import boto3
import os
import shutil
import re
import json

import sqlalchemy as db
import pandas as pd

import access_info as info
from utils import extract_task_id, path_join, is_third_party_outsourced, find_files_in_dir
import local_config as cfg

from rename.correct.correct_id import (CorrectIdDigits, AddTaskId, CorrectIdMaually,
                                     AddTaskCode, CorrectDelimiter, CorrectIdBracket)
from rename.correct.correct_etc import (CorrectSpace)
from . import AwsS3Uploader

#####
complete = "확인 완료"
#####

def generate_rule(
    ver,
    date,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    Prefix
):
    pass


def upload_rule(
    ver,
    date,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    Prefix
):
    save_path = cfg.RULE_DIR_ORIGIN.format(ver, date)
    edit_path = cfg.RULE_DIR_EDIT.format(ver, date)
    engine = db.create_engine(info.url)

    rules: pd.DataFrame = pd.read_sql(info.rule_query, engine)
    rules.sort_values(by="group_nm")

    # 구문 검사 완료한 데이터셋만 필터링

    def get_diagnosed_hist() -> pd.DataFrame:
        diagnosis_hist: pd.DataFrame = pd.read_sql(info.syntax_query, engine)
        has_diagnosed_cond: pd.Series = diagnosis_hist["exec_sttus_cd"] == "COMPLETE"
        diagnosed_hist: pd.DataFrame = diagnosis_hist[has_diagnosed_cond].drop_duplicates(
            subset="dgnss_id")
        return diagnosed_hist.loc[:, ["dgnss_id", "exec_sttus_cd"]]

    diagnosed_hist: pd.DataFrame = get_diagnosed_hist()
    rules: pd.DataFrame = pd.merge(
        left=rules,
        right=diagnosed_hist,
        how="left",
        on="dgnss_id")

    has_diagnosed_cond: pd.Series = rules["exec_sttus_cd"] == "COMPLETE"
    diag_datasets: pd.DataFrame = rules[has_diagnosed_cond]

    # 과제 번호 추출

    def except_extract_task_id(text):
        try:
            return extract_task_id(text)
        except AttributeError as e:
            print(e)
            return

    diag_datasets['group_id'] = diag_datasets['group_nm'].apply(
        except_extract_task_id)
    diag_datasets['task_id'] = diag_datasets['dgnss_nm'].apply(
        except_extract_task_id)

    # group_id와 task_id 일치 여부 확인
    according_cond: pd.Series = diag_datasets.loc[:,
                                                  'task_id'] != diag_datasets.loc[:, 'group_id']
    if len(diag_datasets[according_cond]) > 0:
        display(diag_datasets[according_cond])
        raise Exception("group_id와 task_id가 일치하지 않는 과제가 있습니다.")

    # 사전/최종, 확인 완료 필터링
    # 사전, 최종 구분하기

    def extract_version(text):
        ver = text.split("_")[-1]
        assert ver in ["사전", "최종"], f"{text}에 \"사전\", \"최종\"이 없습니다."
        return ver

    diag_datasets.loc[:, 'ver'] = diag_datasets.loc[:, 'group_nm'].apply(extract_version)
    ver_cond: pd.Series = diag_datasets['ver'] == ver

    # 확인 완료 구분하기
    data_info: pd.DataFrame = pd.read_csv(
        cfg.DATA_INFO_PATH.format(ver), encoding='cp949')
    complete_id_list: pd.Series = data_info['number'][data_info[date] == complete].tolist(
    )
    complete_cond = diag_datasets["task_id"].apply(
        lambda x: x in complete_id_list)

    # 필터링
    target_datasets: pd.DataFrame = diag_datasets[(ver_cond) & (complete_cond)]

    # 파일명 생성
    # 데이터셋명 수정

    def correct_id(text, correctors: list):
        for corrector in correctors:
            text = corrector.execute(text, data_info)
        return text

    corrected: pd.Series = target_datasets['dgnss_nm'].apply(lambda x: correct_id(x, [
        CorrectIdDigits,
        CorrectDelimiter,
        AddTaskId,
        CorrectIdMaually,
        AddTaskCode,
        CorrectIdBracket,
        CorrectSpace,
    ]))

    # 과제 번호 검증
    id_list: list = data_info['number'].tolist()
    id_valid_cond: pd.Series = corrected.apply(
        extract_task_id).apply(lambda x: x not in id_list)
    if len(target_datasets[id_valid_cond]) > 0:
        display(target_datasets[id_valid_cond])
        raise Exception("과제 번호가 유효하지 않은 데이터셋이 있습니다.")

    # 파일명 생성

    def _replace_slash(text):
        if '/' not in text:
            return text

        print("before:", text)
        text = text.replace("/", "·")
        print("after:", text)
        return text

    def _naming(text):
        finder = re.compile(f"^\[{cfg.ID_FORMAT}-{cfg.CATEGORY_FORMAT}\] ")
        find = finder.search(text)
        if find is None:
            raise Exception(f"{text}에 유효한 task_id가 없습니다.")
        idx = find.end()
        text = text[:idx] + f"{ver}검사규칙_" + text[idx:]
        return text

    corrected_name = corrected.apply(_replace_slash)
    corrected_name = corrected_name.apply(_naming)

    # 검사 규칙 생성
    target_datasets.loc[:, 'corrected'] = corrected_name

    for name, rule in zip(
        target_datasets.loc[:, 'corrected'].tolist(),
        target_datasets.loc[:, 'dgnss_rule'].tolist()
    ):
        if is_third_party_outsourced(name):
            continue

        with open(path_join(save_path, name+".json"), "w") as outfile:
            json_date = json.loads(rule)
            json.dump(json_date, outfile, indent='\t', allow_nan=False)

    # 제 3자 품질 검사 규칙
    # 검사 결과 디렉토리에서 json 데이터 불러오기
    json_files = find_files_in_dir(
        cfg.RESULT_DIR_ORIGINAL.format(ver, date), pattern='\.json$')

    # 확인완료 필터링
    json_files = list(filter(lambda x: extract_task_id(x)
                             in complete_cond, json_files))

    # 저장
    def extract_task_id_code(text):
        id_format = "\d-\d{3}-\d{3}-[A-Z]{2}"
        finder = re.compile(id_format)
        id_code = finder.search(text)
        if id_code is None:
            raise AttributeError(
                f"\"{text}\"에 유효한 과제 번호[x-xxx-xxx-xx]가 포함되지 않았습니다.")
        return id_code.group()

    def get_dataset_name_id(id):
        body_name = data_info[data_info['number'] == id]['name']
        if len(body_name) == 0:
            raise Exception
        if len(body_name) >= 2:
            raise Exception
        return body_name.tolist()[0]

    for json_file in json_files:
        file_name = json_file.split("/")[-1]
        body_name = get_dataset_name_id(extract_task_id(json_file))
        file_name = f"[{extract_task_id_code(json_file)}] 사전검사규칙_{body_name}_{file_name}"
        new_file = path_join(save_path, file_name)
        if os.path.exists(new_file):
            continue
        shutil.copy(json_file, new_file)

    # target dir에 copy
    for json_file in find_files_in_dir(save_path, pattern="^.*\.json$"):
        copy_path = path_join(edit_path, json_file.split("/")[-1])
        if os.path.exists(copy_path):
            continue
        shutil.copy(json_file, copy_path)

    # 규칙 업로드
    ## 디렉토리 검증
    rule_files = find_files_in_dir(edit_path, pattern="^.*\.json$")
    rule_files_id = list(map(extract_task_id, rule_files))
    assert len(set(rule_files_id)-set(complete_id_list)
               ) == 0, f"{edit_path}에 확인 완료되지 않은 과제의 검사 규칙이 포함되어 있습니다.\n{set(rule_files_id)-set(complete_id_list)}"
    if len(set(complete_id_list)-set(rule_files_id)) != 0:
        print(f"{edit_path}에 확인 완료된 과제의 검사 규칙({len(set(complete_id_list)-set(rule_files_id))})이 없습니다.\n{set(complete_id_list)-set(rule_files_id)}")
        contn = input("계속 진행하시겠습니까?(Y/N): ")
        assert contn in ["Y", "N"]
        if contn == "N":
            raise
    
    ## 업로드
    uploader = AwsS3Uploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_bucket=aws_bucket,
        Prefix=Prefix
    )

    uploader.upload(
        rule_files,
        ver)

    # # 확인 완료되지 않은 s3 검사규칙 오브젝트 삭제

    # s3_client = boto3.client(
    #     service_name="s3",
    #     aws_access_key_id=aws_access_key_id,
    #     aws_secret_access_key=aws_secret_access_key,
    # )

    # def find_s3_objects(s3_client, bucket_name, prefix):
    #     response = s3_client.list_objects(
    #         Bucket=aws_bucket,
    #         Prefix=Prefix,
    #         Delimiter='/')
    #     object_list = []
    #     # sub_prefix_list = []

    #     if 'Contents' in response:
    #         for content in response['Contents']:
    #             key = content['Key']
    #             idx = key.rindex('/')

    #             if key[:idx + 1] == prefix and key != prefix:
    #                 object_list.append(key)
    #                 continue

    #         # sub_prefix_list.append(key)

    #     try:
    #         sub_prefix_list = [o.get('Prefix')
    #                            for o in response.get('CommonPrefixes')]
    #     except TypeError as e:
    #         return object_list

    #     for sub_prefix in sub_prefix_list:
    #         if "검사 대상 데이터" in sub_prefix:
    #             continue
    #         object_list.extend(find_s3_objects(s3_client, bucket_name, sub_prefix))
    #     # for object in object_list
    #     return object_list

    # 취합본 = find_s3_objects(
    #     s3_client,
    #     aws_bucket,
    #     path_join(Prefix, '취합본/')
    # )
    # 과제별 = find_s3_objects(
    #     s3_client,
    #     aws_bucket,
    #     path_join(Prefix, '과제별/')
    # )

    # 취합본 = list(filter(lambda x: x[-4:] == 'json', 취합본))
    # 과제별 = list(filter(lambda x: x[-4:] == 'json', 과제별))

    # 취합본 = list(filter(lambda x: extract_task_id(x) not in complete_cond, 취합본))
    # 과제별 = list(filter(lambda x: extract_task_id(x) not in complete_cond, 과제별))

    # s3 = boto3.resource(
    #     's3',
    #     aws_access_key_id=aws_access_key_id,
    #     aws_secret_access_key=aws_secret_access_key)

    # for s3_object in tqdm(취합본+과제별, total=len(취합본)+len(과제별)):
    #     s3.Object(aws_bucket, s3_object).delete()


if __name__ == "__main__":
    ###########################
    # Config
    ver = "사전"
    date = "11.23"

    aws_dict = {
        "aws_access_key_id": info.ACCESS_KEY_ID,
        "aws_secret_access_key": info.SECRET_ACCESS_KEY,
        "aws_bucket": info.BUCKET_NAME,
        "Prefix": info.ROOT
    }
    ###########################

    upload_rule(ver, date, **aws_dict)
