import os
import cloudinary
import cloudinary.uploader


def init_cloudinary():
    """
    Cloudinary can be configured using:
    - CLOUDINARY_URL (recommended) OR
    - CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
    """
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    if cloudinary_url:
        cloudinary.config(cloudinary_url=cloudinary_url, secure=True)
        return

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def upload_file(file_storage, folder: str):
    """
    Uploads a Flask file (werkzeug FileStorage) to Cloudinary.
    Returns: (secure_url, public_id)
    """
    init_cloudinary()
    result = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        resource_type="auto",
        overwrite=False,
        unique_filename=True,
    )
    return result.get("secure_url"), result.get("public_id")
