from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from fastapi import UploadFile
import uuid


class S3Client:
    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 bucket_name: str,
                 endpoint_url: str
                 ):
        self.config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'endpoint_url': endpoint_url
        }

        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client('s3', **self.config) as s3_client:
            yield s3_client

    async def upload_file(self, photo: UploadFile, user_id: int, role: str):
        async with self.get_client() as s3_client:
            file_name = f"{role}/{user_id}/{uuid.uuid4()}.{photo.filename.split('.')[-1]}"
            file_content = await photo.read()
            await s3_client.put_object(Body=file_content, Bucket=self.bucket_name, Key=file_name)

            return file_name
