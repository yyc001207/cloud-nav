from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.auth.schema import LoginRequest, LogoutRequest
from app.business.auth.service import authenticate_user, create_token_for_user, logout_user
from app.utils.security import verify_token, get_token_from_header
from app.utils.response import success_response, login_success_response
from app.core.exceptions import AuthException

router = APIRouter(prefix="/api/user", tags=["认证"])


@router.post("/login")
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, request.userName, request.password)
    if not user:
        raise AuthException("用户名或密码错误")
    token = await create_token_for_user(request.userName)
    return login_success_response(token)


@router.post("/logout")
async def logout(request: LogoutRequest, authorization: Optional[str] = Header(None)):
    token_str = await get_token_from_header(authorization)
    await verify_token(token_str)
    await logout_user(token_str)
    return success_response(msg="退出成功")

