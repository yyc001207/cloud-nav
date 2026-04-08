from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.redis import is_token_blacklisted
from app.core.exceptions import AuthException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def verify_token(token: str) -> dict:
    if await is_token_blacklisted(token):
        raise AuthException("Token 已失效")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_name: Optional[str] = payload.get("sub")
        if user_name is None:
            raise AuthException("无效的身份认证")
        return payload
    except JWTError:
        raise AuthException("无效的身份认证")


async def get_token_from_header(authorization: Optional[str] = None, token_param: Optional[str] = None) -> str:
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        elif len(parts) == 1:
            return parts[0]
        raise AuthException("认证令牌格式错误")
    elif token_param:
        return token_param
    raise AuthException("未提供认证令牌")
