import os
import re
import boto3
import botocore
from tqdm import tqdm

from utils import path_join, extract_task_id


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
        self.s3_dir = self._get_directories(
            aws_bucket,
            Prefix,
            Delimiter
        )

    def upload(self, file_list, overwrite=False, progress_bar=True):
        to_paths = {}
        print("전체 파일 수:", len(file_list))
        existed_num = 0
        for file_path in file_list:
            # validate
            self._validate_exist(file_path)
            file_name = file_path.split("/")[-1]
            self._validate_name_format(file_name)

            # to_path setting
            task_number = extract_task_id(file_name)
            to_path = self.s3_dir[task_number]
            to_path = path_join(to_path, "사전", "검사 결과서", file_name)

            if self._s3_object_exists(to_path):
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
                self.s3_client.upload_file(file_path, self.aws_bucket, to_path)
                print(to_path)
            except Exception as e:
                print(e)

    def _get_directories(self,
                         aws_bucket,
                         Prefix,
                         Delimiter) -> dict:
        response = self.s3_client.list_objects(
            Bucket=aws_bucket,
            Prefix=Prefix,
            Delimiter=Delimiter)
        s3_dir_list = [o.get('Prefix') for o in response.get('CommonPrefixes')]
        return {extract_task_id(directory): directory for directory in s3_dir_list}

    def _s3_object_exists(self, key):
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

    def _validate_exist(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError(f"{file_path}는 없는 경로입니다.")

    def _validate_name_format(self, file_name):
        id = "\d-\d{3}-\d{3}"
        category = "[A-Z]{2}"
        result_type = "(구문정확성사전검사결과|통계다양성사전검사결과|사전검사형식오류목록|사전검사구조오류목록|사전검사파일오류목록)"
        date = "22(08|09|10|11|12)(31|30|[0-2][0-9])"
        extension = "(xlsx|csv)"
        name_format = f"^\[{id}-{category}\] {result_type}_.+_{date}\.{extension}$"

        validator = re.compile(name_format)
        if validator.match(file_name) is None:
            raise ValueError(f"{file_name}이 유효한 파일명 형식이 아닙니다.")


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
    print(from_files[0])
    # uploader.upload(path_join(root, from_files[0]))
    uploader.upload(
        "W:/2022 TTA/2022 사전 검사 결과서/[1-014-046-NL] 구문정확성사전검사결과_공감형 대화 데이터_220822.xlsx")


# class TargetPathParser():
#     def __
