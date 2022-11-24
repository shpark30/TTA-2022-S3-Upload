import local_config as cfg
from rename import Correct
from utils import path_join, find_files_in_dir
from upload import AwsS3Uploader


def main(
    ver,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    per_task_prefix
):
    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.RESULT_DIR_ORIGINAL, pattern="^((?!증적용).)*$")

    # 파일명 수정 및 New directory로 이동
    correct = Correct(file_list)
    correct.execute()
    correct.copy_to(cfg.RESULT_DIR_EDIT)

    # S3 업로드
    uploader = AwsS3Uploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_bucket=aws_bucket,
        per_task_prefix=per_task_prefix
    )
    upload_list = find_files_in_dir(cfg.RESULT_DIR_EDIT)
    uploader.upload(upload_list, ver)


if __name__ == "__main__":
    import access_info as info
    # main(ver="사전",
    #      aws_access_key_id=info.TEST_ACCESS_KEY_ID,
    #      aws_secret_access_key=info.TEST_SECRET_ACCESS_KEY,
    #      aws_bucket=info.TEST_BUCKET_NAME,
    #      per_task_prefix=path_join(info.ROOT, "과제별/"))

    main(ver="사전",
         aws_access_key_id=info.ACCESS_KEY_ID,
         aws_secret_access_key=info.SECRET_ACCESS_KEY,
         aws_bucket=info.BUCKET_NAME,
         per_task_prefix=path_join(info.ROOT, "과제별/"))
