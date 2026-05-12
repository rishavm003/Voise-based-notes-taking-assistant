import aioboto3
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.access_key = settings.S3_ACCESS_KEY_ID
        self.secret_key = settings.S3_SECRET_ACCESS_KEY
        self.bucket_name = settings.S3_BUCKET_NAME
        self.public_url = settings.S3_PUBLIC_URL

    async def upload_file(self, file_path: str, object_name: str, content_type: str = "audio/mpeg") -> Optional[str]:
        """
        Uploads a file to Cloudflare R2 / S3 bucket.
        Returns the public URL or the object key.
        """
        if not all([self.endpoint_url, self.access_key, self.secret_key]):
            logger.error("S3 credentials not fully configured.")
            return None

        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name="auto"  # Cloudflare R2 uses 'auto'
            ) as s3:
                with open(file_path, "rb") as data:
                    await s3.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=data,
                        ContentType=content_type
                    )
                
                logger.info(f"Successfully uploaded {object_name} to R2.")
                
                # If a public URL is configured, return the full URL
                if self.public_url:
                    return f"{self.public_url.rstrip('/')}/{object_name}"
                
                return object_name

        except Exception as e:
            logger.error(f"Error uploading to R2: {e}")
            return None

    async def delete_file(self, object_name: str) -> bool:
        """
        Deletes a file from the S3 bucket.
        """
        try:
            async with self.session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name="auto"
            ) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=object_name)
                logger.info(f"Successfully deleted {object_name} from R2.")
                return True
        except Exception as e:
            logger.error(f"Error deleting from R2: {e}")
            return False

# Singleton instance
storage = S3Storage()
