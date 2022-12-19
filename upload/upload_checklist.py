import pandas as pd

import local_config as cfg
from utils import find_files_in_dir
from upload import AwsS3Uploader


def upload_checklist(
    ver,
    date,
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket,
    Prefix
):
    # S3 업로드
    uploader = AwsS3Uploader(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_bucket=aws_bucket,
        Prefix=Prefix
    )
    upload_list = find_files_in_dir(cfg.REPORT_DIR_EDIT.format(ver, date), pattern="^.*\.docx$")
    uploader.upload(upload_list, ver)
