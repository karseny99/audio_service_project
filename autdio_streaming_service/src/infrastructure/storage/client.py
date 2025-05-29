from aiobotocore.session import get_session  # Для асинхронного S3
from typing import Optional

class S3Client:  
    def __init__(
        self,
        endpoint_url: str,          # http://minio:9000
        aws_access_key_id: str,     # Логин 
        aws_secret_access_key: str, # Пароль 
        bucket_name: str,
        region: Optional[str] = None
    ):
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.region = region or "us-east-1"
        self._session = get_session()

    async def get_object(self, key: str, range_header: str = "") -> dict:
        async with self._session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region
        ) as client:
            params = {
                "Bucket": self.bucket_name,
                "Key": key
            }
            if range_header:
                params["Range"] = range_header

            response = await client.get_object(**params)
            return response