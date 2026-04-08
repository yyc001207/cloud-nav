from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.transfer.schema import (
    TextTransferCreateRequest, TextTransferUpdateRequest,
    FileTransferCreateRequest, FileCompleteRequest, TransferListRequest,
)
from app.business.transfer.service import (
    create_text_transfer, get_text_transfers_by_user, get_text_transfers_by_date,
    update_text_transfer, delete_text_transfer,
    create_file_transfer, upload_chunk, complete_upload,
    get_file_transfers_by_user, delete_file_transfer,
)
from app.utils.response import success_response, paginated_response
from app.core.exceptions import NotFoundException
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/transfer", tags=["中转站"])


@router.post("/text/list")
async def list_text_transfers(request: TransferListRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    if request.date:
        texts = await get_text_transfers_by_date(session, user_id, request.date)
    else:
        texts = await get_text_transfers_by_user(session, user_id)
    return success_response(texts)


@router.post("/text/add")
async def add_text_transfer(request: TextTransferCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    text = await create_text_transfer(session, data, user_id)
    return success_response(text)


@router.post("/text/update")
async def update_text_transfer_route(request: TextTransferUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    text = await update_text_transfer(session, request.id, data, user_id)
    if not text:
        raise NotFoundException("文本中转")
    return success_response(text)


@router.post("/text/delete")
async def delete_text_transfer_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await delete_text_transfer(session, id, user_id)
    if not success:
        raise NotFoundException("文本中转")
    return success_response(msg="删除成功")


@router.post("/file/create")
async def create_file_transfer_route(request: FileTransferCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    file = await create_file_transfer(session, data, user_id)
    return success_response(file)


@router.post("/file/chunk")
async def upload_file_chunk(fileId: int = None, chunkIndex: int = None, chunk: bytes = None, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await upload_chunk(session, fileId, chunkIndex, chunk, user_id)
    return success_response(msg="分片上传成功" if success else "分片上传失败")


@router.post("/file/complete")
async def complete_file_upload(request: FileCompleteRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await complete_upload(session, request.fileId, request.totalChunks, user_id)
    return success_response(msg="文件合并成功" if success else "文件合并失败")


@router.post("/file/list")
async def list_file_transfers(request: TransferListRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    files, total = await get_file_transfers_by_user(session, user_id, request.pageNum, request.pageSize)
    return paginated_response(files, total)


@router.post("/file/delete")
async def delete_file_transfer_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await delete_file_transfer(session, id, user_id)
    if not success:
        raise NotFoundException("文件中转")
    return success_response(msg="删除成功")
