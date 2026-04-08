from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.auth.schema import LoginRequest, RegisterRequest
from app.business.auth.service import authenticate_user, create_token_for_user
from app.business.user.service import create_user, get_user_by_name
from app.utils.security import verify_token, get_token_from_header
from app.utils.response import success_response, error_response, login_success_response
from app.core.exceptions import AuthException, ValidationException

router = APIRouter(prefix="/api/user", tags=["认证"])


@router.post("/login")
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, request.userName, request.password)
    if not user:
        raise AuthException("用户名或密码错误")
    token = await create_token_for_user(request.userName)
    return login_success_response(token)


@router.post("/register")
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    user = await create_user(session, request.userName, request.password, request.isActive)
    return success_response(user)
