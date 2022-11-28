import os
import re
import boto3
import botocore
from tqdm import tqdm

import access_info as info
from utils import path_join, extract_task_id, validate_name_format, extract_report_type


class AwsS3Uploader():
    def __init__(self,
                 aws_access_key_id,
                 aws_secret_access_key,
                 aws_bucket,
                 Prefix,
                 Delimiter='/'):

        # S3 접근 정보
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_bucket = aws_bucket
        self.Prefix = Prefix
        self.Delimiter = Delimiter

        # S3 리소스
        self.s3_resource = boto3.resource('s3',
                                          aws_access_key_id=self.aws_access_key_id,
                                          aws_secret_access_key=self.aws_secret_access_key)

        # S3 클라이언트
        self.s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        # S3 이관 디렉토리
        self.per_task_paths_dict = self.__get_task_directories(
            self.aws_bucket,
            self.Prefix,
            self.Delimiter
        )

    def upload(self, file_list, ver, overwrite=False, progress_bar=True):
        assert ver in ["사전", "최종"]
        upload_mode = {
            "과제별": self.__get_path_per_task,
            "취합본": self.__get_path_per_type
        }

        print("전체 파일 수:", len(file_list))
        for mode, get_method in upload_mode.items():
            print(mode, "업로드")
            self.__upload(get_method, file_list, ver, overwrite, progress_bar)
            print()

    def __upload(self, get_method, file_list, ver, overwrite, progress_bar):
        existed_num = 0
        to_paths = {}
        # per task upload
        for file_path in file_list:
            # validate
            self.__validate_file_exist_in_local(file_path)
            file_name = file_path.split("/")[-1]
            validate_name_format(file_name)

            # path setting
            to_path = get_method(file_name, ver)

            if self.__is_s3_object_exists(to_path):
                existed_num += 1
                if not overwrite:
                    continue
            to_paths[file_path] = to_path

        print("이미 업로드된 파일 수:", existed_num)

        if progress_bar:
            bar = tqdm(to_paths.items(), total=len(to_paths))
        else:
            bar = to_paths.items()

        for file_path, to_path in bar:
            try:
                self.s3_client.upload_file(
                    file_path, self.aws_bucket, to_path)
            except Exception as e:
                print(e)

    def __get_path_per_task(self, file_name, ver):
        task_number = extract_task_id(file_name)
        per_task_path = self.per_task_paths_dict[task_number]
        per_task_path = path_join(per_task_path, ver, "검사 결과서")
        self.__validate_s3_object_exists(per_task_path)
        return path_join(per_task_path, file_name)

    def __get_path_per_type(self, file_name, ver):
        root = path_join(info.ROOT, "취합본")

        if self.__is_third_party_outsourced(file_name):
            root = path_join(root, "기타", "제3자검증")

        per_type_path = None
        report_type = extract_report_type(file_name)

        if report_type in [
            "구문정확성사전검사결과",
            "통계다양성사전검사결과",
            "사전검사형식오류목록",
            "사전검사구조오류목록",
            "사전검사파일오류목록"
        ]:
            target_folder_name = f"{ver}검사결과서"
            per_type_path = path_join(root, target_folder_name)

        assert per_type_path is not None
        self.__validate_s3_object_exists(per_type_path)
        per_type_path = path_join(per_type_path, file_name)
        return per_type_path

    def __is_third_party_outsourced(self, file_name):
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

    def __get_task_directories(self,
                               aws_bucket,
                               Prefix,
                               Delimiter) -> dict:
        response = self.s3_client.list_objects(
            Bucket=aws_bucket,
            Prefix=Prefix,
            Delimiter=Delimiter)
        s3_dir_list = [o.get('Prefix') for o in response.get('CommonPrefixes')]
        return {extract_task_id(directory): directory for directory in s3_dir_list}

    def __validate_s3_object_exists(self, key):
        if not self.__is_s3_object_exists(key+"/"):
            raise Exception(f"\"{key}\"가 S3에 없습니다.")

    def __is_s3_object_exists(self, key):
        object = self.s3_resource.Object(self.aws_bucket, key)
        try:
            object.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object dost not exist
                return False
            else:
                # Somthing else has gone wrong
                raise
        else:
            # The object does exist
            return True

    def __validate_file_exist_in_local(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError(f"{file_path}는 없는 경로입니다.")


# Test
if __name__ == "__main__":
    import access_info as info

    uploader = AwsS3Uploader(
        aws_access_key_id=info.TEST_ACCESS_KEY_ID,
        aws_secret_access_key=info.TEST_SECRET_ACCESS_KEY,
        aws_bucket=info.TEST_BUCKET_NAME,
        Prefix=info.TEST_ROOT
    )

    root = r"C:/Users/seohy/workspace/upload_S3/test-data/사전검사결과_new"
    from_files = os.listdir(root)
    # uploader.upload(path_join(root, from_files[0]))
    uploader.upload(
        "W:/2022 TTA/2022 사전 검사 결과서/[1-014-046-NL] 구문정확성사전검사결과_공감형 대화 데이터_220822.xlsx",
        "사전")


# class TargetPathParser():
#     def __
