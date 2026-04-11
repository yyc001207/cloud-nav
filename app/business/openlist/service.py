from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import OpenListGlobalConfigModel, OpenListTaskConfigModel
from app.core.exceptions import NotFoundException, ValidationException
from app.utils.helpers import mask_sensitive_data
from app.core.logger import logger
from datetime import datetime


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "*" * len(token)
    return token[:4] + "*" * (len(token) - 8) + token[-4:]


def global_config_to_response(config: OpenListGlobalConfigModel) -> dict:
    return {
        "id": config.id,
        "userId": config.user_id,
        "baseUrl": config.base_url,
        "videoExtensions": config.video_extensions,
        "subtitleExtensions": config.subtitle_extensions,
        "tokenMasked": _mask_token(config.token),
        "createdAt": config.created_at,
        "updatedAt": config.updated_at,
    }


def global_config_to_dict(config: OpenListGlobalConfigModel) -> dict:
    return {
        "id": config.id,
        "userId": config.user_id,
        "baseUrl": config.base_url,
        "token": config.token,
        "videoExtensions": config.video_extensions,
        "subtitleExtensions": config.subtitle_extensions,
        "createdAt": config.created_at,
        "updatedAt": config.updated_at,
    }


def task_config_to_response(config: OpenListTaskConfigModel) -> dict:
    return {
        "id": config.id,
        "userId": config.user_id,
        "name": config.name,
        "outputDir": config.output_dir,
        "taskPaths": config.task_paths,
        "maxScanDepth": config.max_scan_depth,
        "executionHistory": config.execution_history or [],
        "createdAt": config.created_at,
        "updatedAt": config.updated_at,
    }


def task_config_to_dict(config: OpenListTaskConfigModel) -> dict:
    return {
        "id": config.id,
        "userId": config.user_id,
        "name": config.name,
        "outputDir": config.output_dir,
        "taskPaths": config.task_paths,
        "maxScanDepth": config.max_scan_depth,
        "executionHistory": config.execution_history or [],
        "createdAt": config.created_at,
        "updatedAt": config.updated_at,
    }


async def create_global_config(session: AsyncSession, user_id: int, data: dict) -> dict:
    existing_stmt = select(OpenListGlobalConfigModel).where(
        OpenListGlobalConfigModel.user_id == user_id
    )
    existing = (await session.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise ValidationException("用户已存在 OpenList 全局配置")
    config = OpenListGlobalConfigModel(
        user_id=user_id,
        base_url=data["baseUrl"],
        token=data["token"],
        video_extensions=data.get("videoExtensions"),
        subtitle_extensions=data.get("subtitleExtensions"),
    )
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return global_config_to_response(config)


async def get_global_config(session: AsyncSession, user_id: int) -> Optional[dict]:
    stmt = select(OpenListGlobalConfigModel).where(
        OpenListGlobalConfigModel.user_id == user_id
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    return global_config_to_response(config) if config else None


async def get_global_config_by_id(
    session: AsyncSession, config_id: int, user_id: int
) -> Optional[dict]:
    stmt = select(OpenListGlobalConfigModel).where(
        OpenListGlobalConfigModel.id == config_id,
        OpenListGlobalConfigModel.user_id == user_id,
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    return global_config_to_dict(config) if config else None


async def update_global_config(session: AsyncSession, user_id: int, data: dict) -> dict:
    stmt = select(OpenListGlobalConfigModel).where(
        OpenListGlobalConfigModel.user_id == user_id
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    if not config:
        raise NotFoundException("全局配置")
    field_map = {
        "baseUrl": "base_url",
        "token": "token",
        "videoExtensions": "video_extensions",
        "subtitleExtensions": "subtitle_extensions",
    }
    for camel_key, snake_key in field_map.items():
        if camel_key in data and data[camel_key] is not None:
            setattr(config, snake_key, data[camel_key])
    await session.commit()
    await session.refresh(config)
    return global_config_to_response(config)


async def delete_global_config(session: AsyncSession, user_id: int) -> bool:
    stmt = select(OpenListGlobalConfigModel).where(
        OpenListGlobalConfigModel.user_id == user_id
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    if not config:
        return False
    await session.delete(config)
    await session.commit()
    return True


async def create_task_config(session: AsyncSession, user_id: int, data: dict) -> dict:
    config = OpenListTaskConfigModel(
        user_id=user_id,
        name=data["name"],
        output_dir=data.get("outputDir"),
        task_paths=data["taskPaths"],
        max_scan_depth=data.get("maxScanDepth"),
        execution_history=[],
    )
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return task_config_to_response(config)


async def get_task_config(
    session: AsyncSession, user_id: int, config_id: int
) -> Optional[dict]:
    stmt = select(OpenListTaskConfigModel).where(
        OpenListTaskConfigModel.id == config_id,
        OpenListTaskConfigModel.user_id == user_id,
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    return task_config_to_response(config) if config else None


async def get_task_config_by_id(
    session: AsyncSession, config_id: int, user_id: int
) -> Optional[dict]:
    stmt = select(OpenListTaskConfigModel).where(
        OpenListTaskConfigModel.id == config_id,
        OpenListTaskConfigModel.user_id == user_id,
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    return task_config_to_dict(config) if config else None


async def update_task_config(
    session: AsyncSession, user_id: int, config_id: int, data: dict
) -> dict:
    stmt = select(OpenListTaskConfigModel).where(
        OpenListTaskConfigModel.id == config_id,
        OpenListTaskConfigModel.user_id == user_id,
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    if not config:
        raise NotFoundException("任务配置")
    field_map = {
        "name": "name",
        "outputDir": "output_dir",
        "taskPaths": "task_paths",
        "maxScanDepth": "max_scan_depth",
    }
    for camel_key, snake_key in field_map.items():
        if camel_key in data and data[camel_key] is not None:
            setattr(config, snake_key, data[camel_key])
    await session.commit()
    await session.refresh(config)
    return task_config_to_response(config)


async def delete_task_config(
    session: AsyncSession, user_id: int, config_id: int
) -> bool:
    stmt = select(OpenListTaskConfigModel).where(
        OpenListTaskConfigModel.id == config_id,
        OpenListTaskConfigModel.user_id == user_id,
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    if not config:
        return False
    await session.delete(config)
    await session.commit()
    return True


TASK_CONFIG_ORDER_FIELDS = {
    "createdAt": OpenListTaskConfigModel.created_at,
    "updatedAt": OpenListTaskConfigModel.updated_at,
    "name": OpenListTaskConfigModel.name,
}


async def list_task_configs(
    session: AsyncSession,
    user_id: int,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    name: Optional[str] = None,
    order_by: Optional[str] = None,
    order_dir: Optional[str] = "asc",
) -> tuple[list[dict], int]:
    from sqlalchemy import func as sa_func

    conditions = [OpenListTaskConfigModel.user_id == user_id]
    if name:
        conditions.append(OpenListTaskConfigModel.name.like(f"%{name}%"))
    count_stmt = select(sa_func.count()).where(*conditions)
    total = (await session.execute(count_stmt)).scalar() or 0
    stmt = select(OpenListTaskConfigModel).where(*conditions)
    order_column = TASK_CONFIG_ORDER_FIELDS.get(order_by) if order_by else None
    if order_column is not None:
        stmt = stmt.order_by(
            order_column.desc() if order_dir == "desc" else order_column.asc()
        )
    else:
        stmt = stmt.order_by(OpenListTaskConfigModel.updated_at.desc())
    if page is not None and page_size is not None and page_size > 0:
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(stmt)
    configs = result.scalars().all()
    return [task_config_to_response(c) for c in configs], total


async def add_execution_record(
    session: AsyncSession,
    user_id: int,
    config_id: int,
    success: bool,
    message: str = "",
    **stats,
) -> dict:
    stmt = select(OpenListTaskConfigModel).where(
        OpenListTaskConfigModel.id == config_id,
        OpenListTaskConfigModel.user_id == user_id,
    )
    config = (await session.execute(stmt)).scalar_one_or_none()
    if not config:
        raise NotFoundException("任务配置")
    history = config.execution_history or []
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "success": success,
        "message": message,
        **stats,
    }
    history.append(record)
    if len(history) > 20:
        history = history[-20:]
    config.execution_history = history
    await session.commit()
    await session.refresh(config)
    return task_config_to_response(config)
