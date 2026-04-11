import os
import re
from fastapi import APIRouter, Depends, Header, Request
from typing import Optional
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.transfer.schema import (
    TextTransferCreateRequest,
    TextTransferUpdateRequest,
    FileTransferCreateRequest,
    FileCompleteRequest,
    TransferListRequest,
    FileDownloadRequest,
)
from app.business.transfer.service import (
    create_text_transfer,
    get_text_transfers_by_user,
    get_text_transfers_by_date,
    update_text_transfer,
    delete_text_transfer,
    create_file_transfer,
    upload_chunk,
    complete_upload,
    get_file_transfers_by_user,
    delete_file_transfer,
    get_file_for_download,
    file_chunk_generator,
    get_file_path,
)
from app.utils.response import success_response, paginated_response
from app.core.exceptions import NotFoundException, ValidationException
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/transfer", tags=["中转站"])


@router.post("/text/list")
async def list_text_transfers(
    request: TransferListRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    if request.date:
        texts = await get_text_transfers_by_date(session, user_id, request.date)
        return success_response(texts)
    texts, total = await get_text_transfers_by_user(
        session, user_id, request.pageNum, request.pageSize,
        request.keyword, request.orderBy, request.orderDir
    )
    if request.pageNum is not None and request.pageSize is not None:
        return paginated_response(texts, total)
    return success_response(texts)


@router.post("/text/add")
async def add_text_transfer(
    request: TextTransferCreateRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    text = await create_text_transfer(session, data, user_id)
    return success_response(text)


@router.post("/text/update")
async def update_text_transfer_route(
    request: TextTransferUpdateRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    text = await update_text_transfer(session, request.id, data, user_id)
    if not text:
        raise NotFoundException("文本中转")
    return success_response(text)


@router.post("/text/delete")
async def delete_text_transfer_route(
    id: int,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    success = await delete_text_transfer(session, id, user_id)
    if not success:
        raise NotFoundException("文本中转")
    return success_response(msg="删除成功")


@router.post("/file/create")
async def create_file_transfer_route(
    request: FileTransferCreateRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    file = await create_file_transfer(session, data, user_id)
    return success_response(file)


@router.post("/file/chunk")
async def upload_file_chunk(
    fileId: int = None,
    chunkIndex: int = None,
    chunk: bytes = None,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    success = await upload_chunk(session, fileId, chunkIndex, chunk, user_id)
    return success_response(msg="分片上传成功" if success else "分片上传失败")


@router.post("/file/complete")
async def complete_file_upload(
    request: FileCompleteRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    success = await complete_upload(
        session, request.fileId, request.totalChunks, user_id
    )
    return success_response(msg="文件合并成功" if success else "文件合并失败")


@router.post("/file/list")
async def list_file_transfers(
    request: TransferListRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    files, total = await get_file_transfers_by_user(
        session, user_id, request.pageNum, request.pageSize,
        request.keyword, request.status, request.orderBy, request.orderDir
    )
    if request.pageNum is not None and request.pageSize is not None:
        return paginated_response(files, total)
    return success_response(files)


@router.post("/file/delete")
async def delete_file_transfer_route(
    id: int,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    success = await delete_file_transfer(session, id, user_id)
    if not success:
        raise NotFoundException("文件中转")
    return success_response(msg="删除成功")


def parse_range_header(range_header: str, file_size: int):
    match = re.match(r"bytes=(\d*)-(\d*)", range_header)
    if not match:
        return None
    start_str, end_str = match.group(1), match.group(2)
    if start_str == "" and end_str == "":
        return None
    if start_str == "":
        suffix = int(end_str)
        start = max(0, file_size - suffix)
        end = file_size - 1
    elif end_str == "":
        start = int(start_str)
        end = file_size - 1
    else:
        start = int(start_str)
        end = min(int(end_str), file_size - 1)
    if start > end or start >= file_size:
        return None
    return start, end


@router.post("/file/download")
async def download_file(
    request: FileDownloadRequest,
    fastapi_request: Request,
    authorization: Optional[str] = Header(None),
    range: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_current_user_id(authorization)
    file_record = await get_file_for_download(session, request.fileId, user_id)
    if not file_record:
        raise NotFoundException("文件")
    if file_record.status != "completed":
        raise ValidationException("文件尚未上传完成")
    file_path = get_file_path(request.fileId)
    if not os.path.exists(file_path):
        raise NotFoundException("文件")
    file_size = os.path.getsize(file_path)
    content_type = file_record.content_type or "application/octet-stream"
    filename = file_record.filename
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Accept-Ranges": "bytes",
    }
    if range:
        parsed = parse_range_header(range, file_size)
        if parsed is None:
            return JSONResponse(
                status_code=416,
                content={"code": 416, "msg": "Range 不可满足"},
                headers={"Content-Range": f"bytes */{file_size}"},
            )
        start, end = parsed
        content_length = end - start + 1
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        headers["Content-Length"] = str(content_length)
        return StreamingResponse(
            file_chunk_generator(file_path, start, end),
            status_code=206,
            media_type=content_type,
            headers=headers,
        )
    headers["Content-Length"] = str(file_size)
    return StreamingResponse(
        file_chunk_generator(file_path, 0, file_size - 1),
        status_code=200,
        media_type=content_type,
        headers=headers,
    )
