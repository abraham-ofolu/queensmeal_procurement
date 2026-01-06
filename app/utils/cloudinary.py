import cloudinary
import cloudinary.uploader
import cloudinary.api


def init_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=app.config.get("CLOUDINARY_API_KEY"),
        api_secret=app.config.get("CLOUDINARY_API_SECRET"),
        secure=True
    )


def upload_file(file, folder):
    if not file:
        return None

    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type="auto"
    )
    return result.get("secure_url")


def delete_file(file_url):
    if not file_url:
        return
    try:
        public_id = file_url.split("/")[-1].split(".")[0]
        cloudinary.uploader.destroy(public_id, resource_type="auto")
    except Exception:
        pass
