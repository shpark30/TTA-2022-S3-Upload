from . import CorrectInterface
import re


class CorrectIdDigits(CorrectInterface):
    @classmethod
    def execute(cls, file_name, *args, **kwargs):
        file_name = cls.__correct_digits(file_name)
        return file_name

    @classmethod
    def __correct_digits(cls, file_name) -> bool:
        """
        2-49-175 -> 2-049-175
        """
        format = "\d-\d{2}-\d{3}"
        finder = re.compile(format)
        error = finder.search(file_name)
        if error is None:
            return file_name
        old = error.group()
        new = old.split("-")  # old[:2] + "0" + old[2:]
        new[1] = "0" + new[1]
        new = "-".join(new)
        return file_name.replace(old, new)


class AddTaskId(CorrectInterface):
    """
    페르소나 대화 데이터_형식오류목록_2022-08-25
    -> 아이디 추가
    """
    @classmethod
    def execute(cls, file_name, data_info, *args, **kwargs):
        cls.data_info = data_info
        if cls.__has_task_id(file_name):
            return file_name
        file_name = cls.__add_task_id(file_name)
        return file_name

    @classmethod
    def __has_task_id(cls, file_name) -> bool:
        format = "\d-\d{3}-\d{3}"
        finder = re.compile(format)
        check = finder.search(file_name)
        return check is not None

    @classmethod
    def __add_task_id(cls, file_name):
        data_name = file_name.split("_")[0]
        data_info = cls.data_info[cls.data_info["name"] == data_name]
        if len(data_info) == 0:
            print(file_name)
            raise Exception(f"데이터 이름({data_name})가 master table에 없습니다.")
        if len(data_info) > 1:
            print(file_name)
            raise Exception(f"데이터 이름({data_name})가 master table에 여러 개 들어있습니다.")
        number = data_info['number'].tolist()[0]
        code = data_info['code'].tolist()[0]
        file_name = f"[{number}-{code}] {file_name}"
        return file_name


class CorrectDelimiter(CorrectInterface):
    @classmethod
    def execute(cls, file_name, *args, **kwargs):
        for error_format, correct_method in cls.__get_correct_dict().items():
            error = cls.__find(file_name, error_format)
            if error is None:
                continue
            corrected = correct_method(error)
            file_name = file_name.replace(error, corrected)
        return file_name

    @classmethod
    def __get_correct_dict(cls):
        UNDERSCORE_BEFORE_CODE = "\d-\d{3}-\d{3}_[A-Z]{2}"
        SPACE_BEFORE_CODE = "\d-\d{3}-\d{3}\s[A-Z]{2}"

        correct_dict = {
            UNDERSCORE_BEFORE_CODE: cls.correct_underscore_before_code,
            SPACE_BEFORE_CODE: cls.correct_space_before_code
        }

        return correct_dict

    @classmethod
    def __find(cls, text, pattern):
        finder = re.compile(pattern)
        find = finder.search(text)
        if find is None:
            return None
        return find.group()

    @classmethod
    def correct_underscore_before_code(cls, error):
        """
        [] 안에 연결자 _를 모두 -로 바꾼다.
        ex. [1-002-004_CV] -> [1-002-004-CV]
        """
        return error.replace("_", "-")

    @classmethod
    def correct_space_before_code(cls, error):
        """
        [] 안에 연결자 _를 모두 -로 바꾼다.
        ex. [1-002-004_CV] -> [1-002-004-CV]
        """
        return error.replace(" ", "-")

    # """
    # x-xxx-xxx_AZ -> x-xxx-xxx-AZ
    # """
    # AVAILABLE_PATTERN = "\d-\d{3}-\d{3}-[A-Z]{2}"

    # @classmethod
    # def execute(cls, file_name):
    #     """
    #     [1-001-001_CV] 구문정확성사전검사결과... - > [1-001-001-CV] 구문정확성사전검사결과...
    #     [1-001-001] 구문정확성사전검사결과... - > [1-001-001-CV] 구문정확성사전검사결과...
    #     """
    #     validate_pattern = re.compile(cls.AVAILABLE_PATTERN)
    #     if validate_pattern.search(file_name) is not None:
    #         return file_name

    #     file_name = cls.__correct_underscore_in_task_id(file_name)
    #     file_name = cls.__correct_space_in_task_id(file_name)
    #     return file_name

    # @classmethod
    # def __correct_underscore_in_task_id(cls, file_name):
    #     format = "\d-\d{3}-\d{3}_[A-Z]{2}"
    #     underscore_find_pattern = re.compile(format)
    #     error = underscore_find_pattern.search(file_name)
    #     if error is None:
    #         return file_name
    #     start, end = error.span()
    #     old = file_name[start:end]
    #     new = old.replace("_", "-")
    #     return file_name.replace(old, new)

    # @classmethod
    # def __correct_space_in_task_id(cls, file_name):
    #     format = "\d-\d{3}-\d{3} [A-Z]{2}"
    #     underscore_find_pattern = re.compile(format)
    #     error = underscore_find_pattern.search(file_name)
    #     if error is None:
    #         return file_name
    #     start, end = error.span()
    #     old = file_name[start:end]
    #     new = old.replace(" ", "-")
    #     return file_name.replace(old, new)


class CorrectIdMaually(CorrectInterface):
    @classmethod
    def execute(cls, file_name, *args, **kwargs):
        file_name = cls.__except_correct(file_name)
        return file_name

    @classmethod
    def __except_correct(cls, file_name):
        """ 예외 케이스 처리 """
        except_dict = {
            "2-019-294": "3-019-294",
            "2-062-194": "2-063-194",
            "데2-084-222": "2-084-222",
            "1-007-058_": "1-007-028",
            "2-055-187": "2-057-187",
        }

        for old, new in except_dict.items():
            if old in file_name:
                file_name = file_name.replace(old, new)
        return file_name


class AddTaskCode(CorrectInterface):
    """
    x-xxx-xxx -> x-xxx-xxx-AZ
    """
    CODE_PATTERN = "((?!(\d-\d{3}-\d{3}))\-[A-Z]{2})"
    NO_CODE_PATTERN = "\d-\d{3}-\d{3}"

    @classmethod
    def execute(cls, file_name, data_info):
        """
        _1-001-001_ 구문정확성사전검사결과...
        - > _1-001-001-CV_ 구문정확성사전검사결과...

        [1-001-001_CV] 구문정확성사전검사결과...
        [1-001-001] 구문정확성사전검사결과...
        - > [1-001-001-CV] 구문정확성사전검사결과...
        """
        cls.data_info = data_info
        validate_pattern = re.compile(cls.CODE_PATTERN)
        if validate_pattern.search(file_name) is not None:
            return file_name
        file_name = cls.__add_code_in_task_id(file_name)
        return file_name

    @classmethod
    def __add_code_in_task_id(cls, file_name):
        error_find_pattern = re.compile(cls.NO_CODE_PATTERN)
        task_id = error_find_pattern.search(file_name)
        if task_id is None:
            return file_name
        start, end = task_id.span()
        old = file_name[start:end]
        try:
            new = cls.__add_code_to_number(old)
        except Exception as e:
            print(file_name)
            raise
        return file_name.replace(old, new)

    @classmethod
    def __add_code_to_number(cls, number):
        """ 1-001-001 -> 1-001-001-CV """
        match_series = cls.data_info[cls.data_info['number'] == number].apply(
            lambda row: row[0]+"-"+row[1], axis=1)
        if len(match_series) == 0:
            raise Exception(f"과제 번호({number})가 master table에 없습니다.")
        if len(match_series) > 1:
            raise Exception(f"과제 번호({number})가 master table에 여러 개 들어있습니다.")
        return match_series.tolist()[0]


class CorrectIdBracket(CorrectInterface):
    """
    x-xxx-xxx 통계...
    x-xxx-xxx통계...
    (x-xxx-xxx) 통계...
    _x-xxx-xxx_ 통계...
    x-xxx-xxx_ 통계...

    -> x-xxx-xxx
    """
    AVAILABLE_PATTERN = "^\[\d-\d{3}-\d{3}-[A-Z]{2}\] "

    @classmethod
    def execute(cls, file_name, *args, **kwargs):
        validate_pattern = re.compile(cls.AVAILABLE_PATTERN)
        if validate_pattern.search(file_name) is not None:
            return file_name
        start, end = cls.__extract_task_id_range(file_name)
        # left bracket
        if start == 0:
            file_name = "[" + file_name
            end += 1
        elif start == 1:
            file_name = "[" + file_name[1:]
        elif file_name[:2] == " [":
            file_name = "[" + file_name[2:]
            end -= 1
        else:  # start > 2:
            raise Exception(f"task_id 두번째 글자부터 시작합니다. {file_name}")

        # right bracket
        if file_name[end:end+2] == ")_":
            file_name = file_name[:end] + "]" + file_name[end+2:]
        elif file_name[end:end+2] == "]_":  # "_" : end+1
            file_name = file_name[:end+1] + file_name[end+2:]
        elif file_name[end:end+2] == " _":  # "_" : end+1
            file_name = file_name[:end] + "]" + file_name[end+2:]
        elif file_name[end] in ["_", ")"]:
            file_name = file_name[:end] + "]" + file_name[end+1:]
        elif file_name[end] == " ":
            file_name = file_name[:end] + "]" + file_name[end:]
        elif file_name[end] == "]":
            pass
        else:  # file_name[end+1]에서 띄어쓰기 없이 바로 가는 경우
            file_name = file_name[:end] + "]" + file_name[end:]
        return file_name

    @classmethod
    def __extract_task_id_range(cls, file_name):
        format = "\d{1}-\d{3}-\d{3}-[A-Z]{2}"
        finder = re.compile(format)
        task_id = finder.search(file_name)
        if task_id is None:
            raise Exception(f"{file_name} 에 유효한 과제 아이디가 없습니다.")
        return task_id.span()
