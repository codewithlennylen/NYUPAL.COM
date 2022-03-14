import boto3
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))  # When running the application.

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')

client = boto3.client('s3', # Service we want to use.
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


for file in os.listdir():
    print(f"----- {file} -----")
    if '.py' in file:
        upload_file_bucket = AWS_S3_BUCKET
        upload_file_key = f'verification/{str(file)}'


        # :type Filename: str
        # :param Filename: The path to the file to upload.
        # :type Bucket: str
        # :param Bucket: The name of the bucket to upload to.
        # :type Key: str
        # :param Key: The name of the key to upload to.

        client.upload_file(file, upload_file_bucket, upload_file_key)
        print('Done\n')


# :type Bucket: str
# :param Bucket: The name of the bucket to download from.
# :type Key: str
# :param Key: The name of the key to download from.
# :type Filename: str
# :param Filename: The path to the file to download to.

client.download_file(AWS_S3_BUCKET, 'verification/config.py', 'userManagement/config.py')