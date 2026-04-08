import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.core.logger import logger


async def upload_file(file: UploadFile) -> dict:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}" if file_extension else uuid.uuid4().hex
    file_path = upload_dir / unique_filename
    chunk_size = 1024 * 1024
    total_size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(chunk_size):
            total_size += len(chunk)
            if total_size > settings.MAX_FILE_SIZE:
                file_path.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE} bytes)")
            f.write(chunk)
    file_url = f"/{settings.UPLOAD_DIR}/{unique_filename}"
    logger.info(f"文件上传成功：{unique_filename}, 大小：{total_size} bytes")
    return {"filename": unique_filename, "url": file_url, "size": total_size}


async def upload_files(files: list[UploadFile]) -> list[dict]:
    results = []
    for file in files:
        result = await upload_file(file)
        results.append(result)
    return results
