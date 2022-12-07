import local_config as cfg
from utils import find_files_in_dir
from core.rename_checklist import correct_register
from core.upload import AwsS3Uploader


def upload_checklist(
    ver,
    date,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    Prefix
):
    # 수정할 파일명 찾기
    file_list = find_files_in_dir(
        cfg.RESULT_DIR_ORIGINAL.format(ver, date), pattern="^.*\.docx$")

    # 파일명 수정 및 New directory로 이동
    correct = correct_register(file_list)
    correct.execute()
    correct.remove_older_files(p=True)
    correct.copy_to(cfg.RESULT_DIR_EDIT.format(ver))

    # S3 업로드
    uploader = AwsS3Uploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_bucket=aws_bucket,
        Prefix=Prefix
    )
    upload_list = find_files_in_dir(cfg.RESULT_DIR_EDIT.format(ver))
    uploader.upload(upload_list, ver)
