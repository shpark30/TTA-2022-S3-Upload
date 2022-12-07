import pandas as pd
import os
import re
import local_config as cfg


def get_task_num(file_name: str) -> str:
    ''' [x-xxx-xxx]... -> x-xxx-xxx'''
    numbers = file_name.split('-')[:3]
    numbers[0] = numbers[0][1:]
    numbers[2] = numbers[:3]
    return "-".join(numbers)


def path_join(*args: str, delimiter="/") -> str:
    return os.path.join(*args).replace("\\", delimiter)


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def find_files_in_dir(root, pattern=None):
    reg_pattern = None if pattern is None else re.compile(pattern)
    result = []
    for file in os.listdir(root):
        path = path_join(root, file)
        if os.path.isdir(path):
            # print(path)
            result.extend(find_files_in_dir(path, pattern))
            continue

        if reg_pattern and reg_pattern.match(path) is None:
            continue
        result.append(path)
    return result


def extract_task_id(text: str):
    id_format = "\d-\d{3}-\d{3}"
    finder = re.compile(id_format)
    id = finder.search(text)
    if id is None:
        raise AttributeError(
            f"\"{text}\"에 유효한 과제 번호[x-xxx-xxx]가 포함되지 않았습니다.")
    return id.group()


def extract_report_type(file_name):
    id_type = file_name.split("_")[0]
    report_type = id_type.split("]")[1]  # task id 분리
    report_type = report_type[1:]  # 첫글자 공백 제거
    return report_type


def validate_name_format(file_name):
    # Type
    if not isinstance(file_name, str):
        raise TypeError(f"{file_name}이 유효한 타입(str)이 아닙니다.")

    # Name Format
    validator = re.compile(cfg.FILE_NAME_FORMAT)
    if validator.match(file_name) is None:
        raise ValueError(f"{file_name}이 유효한 파일명 형식이 아닙니다.")


def validate_rule_format(file_name):
    # Type
    if not isinstance(file_name, str):
        raise TypeError(f"{file_name}이 유효한 타입(str)이 아닙니다.")

    # Name Format
    validator = re.compile(cfg.RULE_NAME_FORMAT)
    if validator.match(file_name) is None:
        raise ValueError(f"{file_name}이 유효한 파일명 형식이 아닙니다.")


def is_third_party_outsourced(file_name):
    third_party_outsource = {
        "1-008-030": True,
        "2-005-126": True,
        "2-007-128": True,
        "2-114-255": True,
        "2-073-204": True,
        "2-046-171": True,
        "2-046-172": True,
        "2-056-186": True,
        "3-022-297": True
    }
    task_id = extract_task_id(file_name)
    return third_party_outsource.get(task_id, False)


if __name__ == "__main__":
    result = find_files_in_dir(
        "W:/2022 TTA/2022 사전 검사 결과서/검사 결과/ORIGINAL", "\d-\d{3}-\d{3}")
    print(
        "W:/2022 TTA/2022 사전 검사 결과서/검사 결과/ORIGINAL/[1-026-073-HC]구문정확성검사_인공호흡기 작동 데이터_221025/[1-026-073-HC]구문정확성검사_인공호흡기 작동 데이터 (메타데이터 ventilator)_221025.xlsx" in result)
