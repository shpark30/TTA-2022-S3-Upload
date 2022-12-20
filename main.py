import os
import re
import pandas as pd

import local_config as cfg
import access_info as info

from unzip import unzip_result, unzip_checklist
from rename.rename_result import rename_result
from rename.rename_checklist import rename_checklist
from upload.upload_rule import generate_rule, upload_rule
from upload.upload_result import upload_result
from upload.upload_checklist import upload_checklist


def get_inputs():
    # Test 여부
    while 1:
        test = input("테스트 여부를 선택하세요(Y, N): ")
        if test not in ["Y", "N"]:
            print("Y 혹은 N만 입력하세요.")
            continue
        test = test == "Y"
        break

    aws_dict = {}
    if test:
        aws_dict["aws_access_key_id"] = info.TEST_ACCESS_KEY_ID
        aws_dict["aws_secret_access_key"] = info.TEST_SECRET_ACCESS_KEY
        aws_dict["aws_bucket"] = info.TEST_BUCKET_NAME
        aws_dict["Prefix"] = info.TEST_ROOT
    else:
        aws_dict["aws_access_key_id"] = info.ACCESS_KEY_ID
        aws_dict["aws_secret_access_key"] = info.SECRET_ACCESS_KEY
        aws_dict["aws_bucket"] = info.BUCKET_NAME
        aws_dict["Prefix"] = info.ROOT

    # 사전 / 최종
    while 1:
        ver = input("사전/최종 중 선택하세요: ")
        if ver not in ["사전", "최종"]:
            print("\"사전\" 혹은 \"최종\"만 입력하세요.")
            continue
        break

    # 확인 완료 날짜
    date_validator = re.compile(cfg.MMDD)
    while 1:
        date = input("날짜를 입력해주세요.(mm.dd): ")
        if date_validator.match(date) is None:
            print("날짜 형식이 올바르지 않습니다.")
            continue
        break

    return ver, date, aws_dict


def validate_dirs(ver, date):
    # 디렉토리 검증
    print("디렉토리 검증 시작")
    for p in [
        cfg.DATA_INFO_PATH.format(ver),
        cfg.RESULT_DIR_ORIGINAL.format(ver, date),
        cfg.RESULT_DIR_EDIT.format(ver, date),
        cfg.REPORT_DIR_ORIGINAL.format(ver, date),
        cfg.REPORT_DIR_EDIT.format(ver, date),
        cfg.RULE_DIR_ORIGIN.format(ver, date),
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


def main(ver, date, **kwargs):
    # 결과서 압축 풀기
    print("결과서 압축 풀기")
    unzip_result(ver, date)

    # 체크리스트 압축 풀기
    print("체크리스트 압축 풀기")
    unzip_checklist(ver, date)

    # 검사 규칙 파일 만들기
    print("검사 규칙 생성")
    generate_rule(ver, date)
    print("완료")
    print("="*50)
    
    while 1:
        contn = input("파일명 수정을 진행하시겠습니까?(Y/N): ")
        if contn not in ["Y", "N"]:
            print("\"Y\" 혹은 \"N\"만 입력하세요.")
            continue
        break

    if contn == "N":
        return

    print("완료")
    print("="*50)

    # 이슈리포트 파일명 수정
    print("체크리스트 파일명 수정")
    rename_checklist(ver, date)
    print("완료")
    print("="*50)

    # 검사 결과 파일명 수정
    print("검사 결과서 파일명 수정")
    import pdb
    pdb.set_trace()
    rename_result(ver, date)
    print("완료")
    print("="*50)

    while 1:
        contn = input("업로드를 진행하시겠습니까?(Y/N): ")
        if contn not in ["Y", "N"]:
            print("\"Y\" 혹은 \"N\"만 입력하세요.")
            continue
        break

    # 체크리스트 업로드
    print("체크리스트 업로드")
    upload_checklist(ver, date, **kwargs)
    print("완료")
    print("="*50)

    # 검사 결과서 업로드
    print("검사 결과서 업로드")
    upload_result(ver, date, **kwargs)
    print("완료")
    print("="*50)

    # 검사 규칙 업로드
    print("검사 규칙 업로드")
    upload_rule(ver, date, **kwargs)
    print("완료")
    print("="*50)


if __name__ == "__main__":
    ver, date, aws_dict = get_inputs()
    
    validate_dirs(ver, date)

    main(ver=ver, date=date, **aws_dict)
