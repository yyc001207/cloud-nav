from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from app.business.upload.service import upload_file, upload_files
from app.utils.response import success_response
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/upload", tags=["文件上传"])


@router.post("/file")
async def upload_single_file(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    result = await upload_file(file)
    return success_response(result)


@router.post("/files")
async def upload_multiple_files(files: List[UploadFile] = File(...), user_id: int = Depends(get_current_user_id)):
    results = await upload_files(files)
    return success_response(results)
