from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.auth.schema import LoginRequest, LogoutRequest
from app.business.auth.service import authenticate_user, create_token_for_user, logout_user
from app.utils.security import verify_token, get_token_from_request
from app.utils.response import success_response
from app.core.exceptions import AuthException
from app.core.config import settings

router = APIRouter(prefix="/api/user", tags=["认证"])


def _build_cookie_header(token: str, max_age: int) -> str:
    parts = [
        f"token={token}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        f"Max-Age={max_age}",
    ]
    if settings.COOKIE_DOMAIN:
        parts.append(f"Domain={settings.COOKIE_DOMAIN}")
    if settings.COOKIE_SECURE:
        parts.append("Secure")
    return "; ".join(parts)


def _build_clear_cookie_header() -> str:
    parts = [
        "token=",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        "Max-Age=0",
    ]
    if settings.COOKIE_DOMAIN:
        parts.append(f"Domain={settings.COOKIE_DOMAIN}")
    if settings.COOKIE_SECURE:
        parts.append("Secure")
    return "; ".join(parts)


@router.post("/login")
async def login(request: LoginRequest, response: Response, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, request.userName, request.password)
    if not user:
        raise AuthException("用户名或密码错误")
    token = await create_token_for_user(request.userName)
    max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.headers["Set-Cookie"] = _build_cookie_header(token, max_age)
    return success_response(msg="登录成功")


@router.post("/logout")
async def logout(request: Request, response: Response):
    try:
        token_str = await get_token_from_request(request)
        await verify_token(token_str)
        await logout_user(token_str)
    except Exception:
        pass
    response.headers["Set-Cookie"] = _build_clear_cookie_header()
    return success_response(msg="退出成功")
