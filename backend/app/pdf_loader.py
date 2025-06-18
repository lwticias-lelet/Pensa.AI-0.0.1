import os
from fastapi import UploadFile

UPLOAD_DIR = "backend/data/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    with open(file_path, "wb") as f:
        content = await upload_file.read()
        f.write(content)
    return file_path
