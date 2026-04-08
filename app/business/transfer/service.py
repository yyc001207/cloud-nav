import os
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import TextTransferModel, FileTransferModel
from app.core.exceptions import NotFoundException
from app.core.logger import logger


UPLOAD_DIR = "uploads/transfer"


def text_transfer_to_dict(t: TextTransferModel) -> dict:
    return {
        "id": t.id,
        "content": t.content,
        "title": t.title,
        "userId": t.user_id,
        "createdAt": t.created_at,
        "updatedAt": t.updated_at,
    }


def file_transfer_to_dict(f: FileTransferModel) -> dict:
    return {
        "id": f.id,
        "filename": f.filename,
        "fileSize": f.file_size,
        "fileHash": f.file_hash,
        "contentType": f.content_type,
        "userId": f.user_id,
        "status": f.status,
        "createdAt": f.created_at,
        "updatedAt": f.updated_at,
    }


async def create_text_transfer(session: AsyncSession, data: dict, user_id: int) -> dict:
    text = TextTransferModel(user_id=user_id, content=data["content"], title=data.get("title"))
    session.add(text)
    await session.commit()
    await session.refresh(text)
    return text_transfer_to_dict(text)


async def get_text_transfers_by_user(session: AsyncSession, user_id: int) -> list[dict]:
    stmt = select(TextTransferModel).where(TextTransferModel.user_id == user_id).order_by(TextTransferModel.created_at.asc())
    result = await session.execute(stmt)
    texts = result.scalars().all()
    return [text_transfer_to_dict(t) for t in texts]


async def get_text_transfers_by_date(session: AsyncSession, user_id: int, date_str: str) -> list[dict]:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) - timedelta(microseconds=1)
    stmt = select(TextTransferModel).where(
        TextTransferModel.user_id == user_id,
        TextTransferModel.created_at >= start_of_day,
        TextTransferModel.created_at <= end_of_day,
    ).order_by(TextTransferModel.created_at.asc())
    result = await session.execute(stmt)
    texts = result.scalars().all()
    return [text_transfer_to_dict(t) for t in texts]


async def get_text_transfer_by_id(session: AsyncSession, text_id: int, user_id: int) -> Optional[dict]:
    stmt = select(TextTransferModel).where(TextTransferModel.id == text_id, TextTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    text = result.scalar_one_or_none()
    return text_transfer_to_dict(text) if text else None


async def update_text_transfer(session: AsyncSession, text_id: int, data: dict, user_id: int) -> Optional[dict]:
    stmt = select(TextTransferModel).where(TextTransferModel.id == text_id, TextTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    text = result.scalar_one_or_none()
    if not text:
        return None
    if "title" in data and data["title"] is not None:
        text.title = data["title"]
    await session.commit()
    await session.refresh(text)
    return text_transfer_to_dict(text)


async def delete_text_transfer(session: AsyncSession, text_id: int, user_id: int) -> bool:
    stmt = select(TextTransferModel).where(TextTransferModel.id == text_id, TextTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    text = result.scalar_one_or_none()
    if not text:
        return False
    await session.delete(text)
    await session.commit()
    return True


async def create_file_transfer(session: AsyncSession, data: dict, user_id: int) -> dict:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file = FileTransferModel(
        user_id=user_id,
        filename=data["filename"],
        file_size=data["fileSize"],
        file_hash=data["fileHash"],
        content_type=data["contentType"],
        status="pending",
        chunks_uploaded=0,
        total_chunks=0,
    )
    session.add(file)
    await session.commit()
    await session.refresh(file)
    return file_transfer_to_dict(file)


def get_file_path(file_id: int) -> str:
    return os.path.join(UPLOAD_DIR, str(file_id))


def get_chunk_path(file_id: int, chunk_index: int) -> str:
    return os.path.join(UPLOAD_DIR, f"{file_id}_chunk_{chunk_index}")


async def upload_chunk(session: AsyncSession, file_id: int, chunk_index: int, chunk_data: bytes, user_id: int) -> bool:
    stmt = select(FileTransferModel).where(FileTransferModel.id == file_id, FileTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    file = result.scalar_one_or_none()
    if not file:
        return False
    chunk_path = get_chunk_path(file_id, chunk_index)
    with open(chunk_path, "wb") as f:
        f.write(chunk_data)
    file.chunks_uploaded = (file.chunks_uploaded or 0) + 1
    await session.commit()
    return True


async def complete_upload(session: AsyncSession, file_id: int, total_chunks: int, user_id: int) -> bool:
    stmt = select(FileTransferModel).where(FileTransferModel.id == file_id, FileTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    file = result.scalar_one_or_none()
    if not file:
        return False
    file_path = get_file_path(file_id)
    with open(file_path, "wb") as f:
        for i in range(total_chunks):
            chunk_path = get_chunk_path(file_id, i)
            if os.path.exists(chunk_path):
                with open(chunk_path, "rb") as chunk_file:
                    f.write(chunk_file.read())
                os.remove(chunk_path)
            else:
                return False
    file.status = "completed"
    file.total_chunks = total_chunks
    await session.commit()
    return True


async def get_file_transfers_by_user(session: AsyncSession, user_id: int, page: int = 1, page_size: int = 10) -> tuple[list[dict], int]:
    count_stmt = select(func.count()).where(FileTransferModel.user_id == user_id)
    total = (await session.execute(count_stmt)).scalar() or 0
    stmt = select(FileTransferModel).where(FileTransferModel.user_id == user_id).order_by(FileTransferModel.created_at.asc()).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(stmt)
    files = result.scalars().all()
    return [file_transfer_to_dict(f) for f in files], total


async def get_file_transfer_by_id(session: AsyncSession, file_id: int, user_id: int) -> Optional[dict]:
    stmt = select(FileTransferModel).where(FileTransferModel.id == file_id, FileTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    file = result.scalar_one_or_none()
    return file_transfer_to_dict(file) if file else None


async def delete_file_transfer(session: AsyncSession, file_id: int, user_id: int) -> bool:
    stmt = select(FileTransferModel).where(FileTransferModel.id == file_id, FileTransferModel.user_id == user_id)
    result = await session.execute(stmt)
    file = result.scalar_one_or_none()
    if not file:
        return False
    file_path = get_file_path(file_id)
    if os.path.exists(file_path):
        os.remove(file_path)
    await session.delete(file)
    await session.commit()
    return True
