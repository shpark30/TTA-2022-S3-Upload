import os
import shutil
from collections import OrderedDict, defaultdict
from tqdm import tqdm
from copy import deepcopy
import pandas as pd
import re
from datetime import datetime

import local_config as cfg
from utils import path_join, validate_name_format, extract_task_id


class CorrectInterface:
    def execute(self, *args, **kwargs):
        raise NotImplementedError


class RegistryMetaClass(type):
    def __new__(cls, name, bases, attrs):
        # 클래스를 생성한다.
        new_cls = type.__new__(cls, name, bases, attrs)
        # 클래스의 속성에 REGISTRY가 있다면
        # bases 내에 RegistryMetaClass를 메타 클래스로 활용한 슈퍼 클래스가 있다는 의미로 간주하여
        if hasattr(new_cls, "REGISTRY"):
            # (다중 상속에도 원하는 방식으로 동작하도록)
            for base in bases:
                if hasattr(base, "REGISTRY"):
                    # REGISTRY에 생성된 클래스를 등록한다.
                    base.REGISTRY[name] = new_cls
        # REGISTRY 속성이 없다면
        else:
            # RegistryMetaClass가 메타 클래스로 활용되었으므로 REGISTRY 속성을 부여한다.
            new_cls.REGISTRY = OrderedDict()
        return new_cls


class Correct(CorrectInterface):
    REGISTRY = {}

    def __init__(self, file_list: list):
        assert len(set(file_list)) == len(
            file_list), "파일 리스트에 중복이 있습니다."
        self.old_file_list = file_list
        self.new_file_dict = {}

        self.data_info = None

    def __len__(self):
        if len(self.new_file_dict) == 0:
            return len(self.old_file_list)
        return len(self.new_file_dict)

    @classmethod
    def register(cls, sub_class):
        cls.REGISTRY[sub_class.__name__] = sub_class

    def execute(self, p=False):
        if len(self.new_file_dict):
            print("이미 execute를 실행했습니다.")
            return

        print(self.REGISTRY.keys())

        for file_path in self.old_file_list:
            file_name = file_path.split("/")[-1]
            self.new_file_dict[file_path] = self.correct(file_name, p=p)

    def rename(self, root, p=False, progress_bar: bool = True):
        if not os.path.exists(root):
            print(f"{root} 경로가 존재하지 않습니다.")
            return

        file_list = list(filter(lambda x: x.split(
            ".")[-1] in ["csv", "xlsx"], os.listdir(root)))
        if progress_bar:
            bar = tqdm(file_list, total=len(file_list))
        else:
            bar = file_list

        for old_file in bar:
            old_path = path_join(root, old_file)
            new_path = path_join(root, self.correct(old_file, p=p))
            if os.path.exists(new_path):
                os.remove(new_path)
                continue
            os.rename(old_path, new_path)

    def copy_to(self, root, overwrite=False, progress_bar: bool = True):
        """ 기존 파일의 수정 버전을 root 하위에 옮긴다. """
        if len(self.new_file_dict) == 0:
            print("new_file_dict가 비어있습니다. execute 메서드를 먼저 실행해주시기 바랍니다.")
            return

        if not os.path.exists(root):
            print(f"{root} 경로가 존재하지 않습니다.")
            return

        new_file_dict = deepcopy(self.new_file_dict)
        print("전체 파일 수:", len(new_file_dict))
        existed_num = 0
        remove_keys = []
        for key, new_path in new_file_dict.items():
            if os.path.exists(path_join(root, new_path)):
                existed_num += 1
                if not overwrite:
                    remove_keys.append(key)

        if not overwrite:
            for key in remove_keys:
                del (new_file_dict[key])

        print("이름이 이미 수정된 파일 수:", existed_num)
        print("새로운 파일 수:", len(self.new_file_dict) - existed_num)

        if progress_bar:
            bar = tqdm(new_file_dict.items(),
                       total=len(new_file_dict))
        else:
            bar = new_file_dict.items()

        for old_path, new_name in bar:
            new_path = path_join(root, new_name)
            if not os.path.exists(new_path):
                shutil.copy(old_path, new_path)

    def correct(self, file_path: str, data_info: pd.DataFrame, p=True) -> str:
        self.data_info = data_info
        file_name = file_path.split("\\")[-1]
        prev_name = deepcopy(file_name)
        # if file_path == "페르소나 대화 데이터_형식오류목록_2022-08-25 14_07_54.csv":
        # import pdb
        # pdb.set_trace()
        for name, sub_class in self.REGISTRY.items():
            file_name = sub_class.execute(file_name, data_info)
        try:
            validate_name_format(file_name)
        except Exception as e:
            print("before:", file_path)
            print("after:", file_name)
            raise e

        if p and prev_name != file_name:
            print("기존: " + prev_name)
            print("변경: " + file_name)
            print()
        return file_path.replace(prev_name, file_name)

    def remove_older_files(self, p=False):
        """ 동일한 문서 중 날짜가 최신인 파일 외에는 new_file_dict에서 제거 """
        finder = re.compile(cfg.DATE_FORMAT)

        def _split_by_date(file_name):
            find = finder.search(file_name)
            return (file_name[:find.start()], file_name[find.end():]), find.group()

        # 딕셔너리로 접근하는 것이 좋음
        def _get_datetime(date):
            year = int("20" + date[:2])
            month = int(date[2:4])
            day = int(date[4:6])
            return datetime(year, month, day)

        _dict = defaultdict(dict)
        remove_targets = []
        for old_name, new_name in self.new_file_dict.items():
            except_date, date = _split_by_date(new_name)
            _dict[except_date][date] = old_name
            assert len(_dict[except_date]) <= 2

            if len(_dict[except_date]) == 1:
                continue

            dates = [(_get_datetime(date), date)
                     for date in _dict[except_date].keys()]
            dates.sort()
            older_date = dates[0][1]
            older_file_name = _dict[except_date].pop(older_date)
            remove_targets.append(older_file_name)

            if p:
                newer_date = dates[1][1]
                newer_file_name = _dict[except_date][newer_date]
                print("old 버전:", older_file_name)
                print("최신 버전:", newer_file_name)

        for older_file_name in remove_targets:
            del(self.new_file_dict[older_file_name])

        self.__validate_date

    def __validate_date(self, date):
        if len(self.data_info.columns) == 5:
            return

        def _validate(text):
            validator = re.compile(cfg.MMDD)
            return validator.match(text) is not None
        columns = self.data_info.columns
        assert _validate(columns[-1])
        assert _validate(columns[-2])
        assert date == columns[-1]

        done_cond = self.data_info.iloc[:, -2] == "확인 완료"
        done_tasks = self.data_info.loc[:, "number"][done_cond].tolist()

        curr_cond = self.data_info.iloc[:, -2] == "확인 완료"
        curr_tasks = self.data_info.loc[:, "number"][curr_cond].tolist()

        assert len(set(done_tasks) - set(curr_tasks)
                   ) == 0, f"data_info.csv의 {date}컬럼에 확인 완료되지 않은 과제 중 {columns[-2]}컬럼에 확인 완료된 과제가 있습니다."

        todo_tasks = list(set(curr_tasks) - set(done_tasks))

        assert set(todo_tasks) == set(map(extract_task_id, self.new_file_dict.values(
        ))), f"새로 이관할 파일과 data_info.csv 상 새로 확인 완료된 파일이 다릅니다."


if __name__ == "__main__":
    from utils import find_files_in_dir
    from core.rename_checklist import correct_register
    ver = "사전"
    date = "12.06"

    files = find_files_in_dir(cfg.REPORT_DIR_ORIGINAL.format(
        ver, date), pattern="^.*\.docs$")

    corrector = correct_register(files)
    data_info = pd.read_csv(cfg.DATA_INFO_PATH.format(ver), encoding="cp040")
    corrector.execute()
    corrector.remove_older_files(p=True)
