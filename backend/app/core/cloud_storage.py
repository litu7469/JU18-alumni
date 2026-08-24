"""
Cloud image storage via Cloudinary.

Reads the CLOUDINARY_URL environment variable automatically (the Cloudinary
SDK does this on import — no extra config needed as long as the env var is set
in Railway and/or the local .env file).

Falls back gracefully with a clear error if CLOUDINARY_URL isn't configured,
rather than silently writing to local disk (which is what caused uploaded
photos to disappear after container restarts).
"""
import os
import logging
import cloudinary
import cloudinary.uploader

logger = logging.getLogger(__name__)

_configured = bool(os.getenv("CLOUDINARY_URL"))
if not _configured:
    logger.warning("CLOUDINARY_URL is not set — image uploads will fail until it is configured.")


def upload_image(file_obj, folder: str) -> str:
    """
    Upload a file-like object to Cloudinary under the given folder.
    Returns the secure (https) URL of the uploaded image.
    Raises RuntimeError if Cloudinary isn't configured or the upload fails.
    """
    if not _configured:
        raise RuntimeError("Image storage is not configured (CLOUDINARY_URL missing).")
    try:
        result = cloudinary.uploader.upload(
            file_obj,
            folder=f"ju18-alumni/{folder}",
            resource_type="image",
        )
        return result["secure_url"]
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise RuntimeError("Image upload failed. Please try again.")