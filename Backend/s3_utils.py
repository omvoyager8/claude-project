import boto3
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def upload_to_s3(file_path, key):
    s3.upload_file(file_path, S3_BUCKET, key)

def download_from_s3(key, local_path):
    s3.download_file(S3_BUCKET, key, local_path)