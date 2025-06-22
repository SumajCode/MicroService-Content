import boto3
from config.settings import Config

class ServicioCloudflareR2:

    def __init__(self):
        self.idAccount = Config.CLOUD_ACCOUNT_ID
        self.accessKeyId = Config.CLOUD_ACCESS_KEY_ID
        self.secretAccessKey = Config.CLOUD_SECRET_ACCESS_KEY
        self.r2BucketName = Config.CLOUD_R2_BUCKET_NAME
    
    def connectionR2(self):
        s3 = boto3.client(
            's3',
            endpoint_url=f'https://{self.idAccount}.r2.cloudflarestorage.com',
            aws_access_key_id=self.accessKeyId,
            aws_secret_access_key=self.secretAccessKey,
            region_name='auto')