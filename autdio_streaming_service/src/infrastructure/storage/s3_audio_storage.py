from typing import AsyncGenerator

from src.domain.stream.repository import AudioStorage
from src.infrastructure.storage.client import S3Client

from src.core.config import settings

class S3AudioStorage(AudioStorage):
    def __init__(self, s3_client: S3Client, bucket_name: str):
        self.s3 = s3_client
        self.bucket = bucket_name

    async def get_chunks(
        self, 
        track_id: str, 
        bitrate: int, 
        offset: int = 0,
        chunk_size: int = 1024 * 64
    ) -> AsyncGenerator[bytes, None]:
        s3_key = f"{settings.MINIO_TRACK_PATH}/{track_id}/{bitrate}kbps.mp3"
        
        async with self.s3.get_object(
            Bucket=self.bucket,
            Key=s3_key,
            Range=f"bytes={offset}-"
        ) as response:
            async for chunk in response["Body"].iter_chunks(chunk_size):
                yield chunk