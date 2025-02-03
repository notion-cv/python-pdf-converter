import boto3

# S3 클라이언트 초기화
s3_client = boto3.client('s3')

def download_zip(bucket: str, file_key: str, local_path: str) -> None:
    """S3에서 ZIP 파일 다운로드"""
    try:
        s3_client.download_file(bucket, file_key, local_path)
    except Exception as e:
        raise

def upload_pdf(local_path: str, bucket: str, file_key: str) -> None:
    """변환된 PDF를 S3에 업로드"""
    try:
        s3_client.upload_file(local_path, bucket, file_key)
    except Exception as e:
        raise