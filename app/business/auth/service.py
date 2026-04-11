from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import UserModel
from app.core.exceptions import AuthException, ValidationException
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.core.redis import blacklist_token


async def authenticate_user(session: AsyncSession, user_name: str, password: str) -> Optional[dict]:
    stmt = select(UserModel).where(UserModel.user_name == user_name)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    if not user.is_active:
        raise AuthException("用户已被禁用")
    return _user_to_dict(user)


async def create_token_for_user(user_name: str) -> str:
    return create_access_token(data={"sub": user_name})


def _user_to_dict(user: UserModel) -> dict:
    return {
        "id": user.id,
        "userName": user.user_name,
        "isActive": user.is_active,
        "createdAt": user.created_at,
        "updatedAt": user.updated_at,
    }


async def logout_user(token: str) -> None:
    from jose import jwt
    from app.core.config import settings
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    exp = payload.get("exp", 0)
    remaining_seconds = max(int(exp - datetime.utcnow().timestamp()), 0)
    if remaining_seconds > 0:
        await blacklist_token(token, ttl=remaining_seconds)
