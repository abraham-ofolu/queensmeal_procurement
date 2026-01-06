import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_file(file, folder):
    result = cloudinary.uploader.upload(
        file,
        folder=f"queensmeal/{folder}",
        resource_type="auto"
    )
    return result["secure_url"]

def delete_file(url):
    public_id = url.split("/")[-1].split(".")[0]
    cloudinary.uploader.destroy(public_id, resource_type="auto")
