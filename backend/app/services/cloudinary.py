import cloudinary
import cloudinary.uploader
import logging
from uuid import uuid4
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Cloudinary using URL
if settings.CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
else:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

async def upload_audio(file_path: str, user_id: str) -> dict:
    """
    Uploads audio file to Cloudinary.
    """
    try:
        # User requested resource_type="raw" for this version
        upload_result = cloudinary.uploader.upload(
            file_path,
            folder=f"voice-notes/{user_id}",
            resource_type="raw",
            use_filename=False,
            unique_filename=True
        )
        return {
            "url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id")
        }
    except Exception as e:
        logger.error(f"Cloudinary upload failure: {e}")
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

async def delete_audio(public_id: str) -> bool:
    """
    Deletes audio by public_id from Cloudinary.
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="raw")
        return result.get("result") == "ok"
    except Exception as e:
        logger.warning(f"Cloudinary deletion failed for {public_id}: {e}")
        return False
