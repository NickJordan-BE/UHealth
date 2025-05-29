import boto3, os

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

BUCKET = "placeholder"

# Downloads CNN model from s3 bucket for mounting on prediction api call
def download_model_from_s3(local_path, s3_key):
    s3.download_file(BUCKET, s3_key, local_path)