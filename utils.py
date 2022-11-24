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
        if path.split(".")[-1] in ["csv", "xlsx"]:
            if reg_pattern and reg_pattern.search(path) is None:
                continue
            result.append(path)
            continue
    return result


def extract_task_id(input: str):
    id_format = "\d-\d{3}-\d{3}"
    finder = re.compile(id_format)
    try:
        start, end = finder.search(input).span()
    except AttributeError as e:
        raise AttributeError(
            f"\"{input}\"에 유효한 과제 번호[x-xxx-xxx]가 포함되지 않았습니다.")
    return input[start:end]


def validate_name_format(file_name):
    validator = re.compile(cfg.FILE_NAME_FORMAT)
    if validator.match(file_name) is None:
        raise ValueError(f"{file_name}이 유효한 파일명 형식이 아닙니다.")


if __name__ == "__main__":
    result = find_files_in_dir(
        "W:/2022 TTA/2022 사전 검사 결과서/검사 결과/ORIGINAL", "\d-\d{3}-\d{3}")
    print(
        "W:/2022 TTA/2022 사전 검사 결과서/검사 결과/ORIGINAL/[1-026-073-HC]구문정확성검사_인공호흡기 작동 데이터_221025/[1-026-073-HC]구문정확성검사_인공호흡기 작동 데이터 (메타데이터 ventilator)_221025.xlsx" in result)
