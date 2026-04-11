from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import UserModel
from app.core.exceptions import NotFoundException, ValidationException
from app.utils.security import get_password_hash


def user_to_dict(user: UserModel) -> dict:
    return {
        "id": user.id,
        "userName": user.user_name,
        "isActive": user.is_active,
        "createdAt": user.created_at,
        "updatedAt": user.updated_at,
    }


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[dict]:
    user = await session.get(UserModel, user_id)
    if not user:
        return None
    return user_to_dict(user)


async def get_user_by_name(session: AsyncSession, user_name: str) -> Optional[dict]:
    stmt = select(UserModel).where(UserModel.user_name == user_name)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return None
    return user_to_dict(user)


async def update_user(session: AsyncSession, user_id: int, update_data: dict) -> dict:
    user = await session.get(UserModel, user_id)
    if not user:
        raise NotFoundException("用户")
    if "userName" in update_data and update_data["userName"] is not None:
        user.user_name = update_data["userName"]
    if "password" in update_data and update_data["password"] is not None:
        user.password = get_password_hash(update_data["password"])
    if "isActive" in update_data and update_data["isActive"] is not None:
        user.is_active = update_data["isActive"]
    await session.commit()
    await session.refresh(user)
    return user_to_dict(user)
