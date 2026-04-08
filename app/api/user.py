from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.user.service import get_user_by_id, update_user
from app.business.user.schema import UserUpdateRequest
from app.utils.security import verify_token, get_token_from_header
from app.utils.response import success_response, error_response
from app.core.exceptions import AuthException, NotFoundException

router = APIRouter(prefix="/api/user", tags=["用户"])


async def get_current_user_id(authorization: Optional[str] = Header(None), token: Optional[str] = None) -> int:
    token_str = await get_token_from_header(authorization, token)
    payload = await verify_token(token_str)
    user_name = payload.get("sub")
    if not user_name:
        raise AuthException()
    from app.business.user.service import get_user_by_name
    from app.core.database import get_session
    session = get_session()
    try:
        user = await get_user_by_name(session, user_name)
        if not user:
            raise NotFoundException("用户")
        return user["id"]
    finally:
        await session.close()


@router.post("/userInfo")
async def get_user_info(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    user = await get_user_by_id(session, user_id)
    if not user:
        raise NotFoundException("用户")
    return success_response(user)


@router.post("/update")
async def update_user_info(request: UserUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    update_data = request.model_dump(exclude_unset=True, exclude_none=True)
    user = await update_user(session, user_id, update_data)
    return success_response(user)
