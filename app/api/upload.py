from fastapi import APIRouter, Depends, UploadFile, File, Header
from typing import Optional, List
from app.business.upload.service import upload_file, upload_files
from app.utils.response import success_response
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/upload", tags=["文件上传"])


@router.post("/file")
async def upload_single_file(file: UploadFile = File(...), authorization: Optional[str] = Header(None)):
    await get_current_user_id(authorization)
    result = await upload_file(file)
    return success_response(result)


@router.post("/files")
async def upload_multiple_files(files: List[UploadFile] = File(...), authorization: Optional[str] = Header(None)):
    await get_current_user_id(authorization)
    results = await upload_files(files)
    return success_response(results)
