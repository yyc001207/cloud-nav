from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.user.service import get_user_by_id, update_user, get_user_by_name
from app.business.user.schema import UserUpdateRequest
from app.utils.security import verify_token, get_token_from_request
from app.utils.response import success_response, error_response
from app.core.exceptions import AuthException, NotFoundException

router = APIRouter(prefix="/api/user", tags=["用户"])


async def get_current_user_id(request: Request) -> int:
    token_str = await get_token_from_request(request)
    payload = await verify_token(token_str)
    user_name = payload.get("sub")
    if not user_name:
        raise AuthException()
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
async def get_user_info(user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_session)):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise NotFoundException("用户")
    return success_response(user)


@router.post("/update")
async def update_user_info(request: UserUpdateRequest, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_session)):
    update_data = request.model_dump(exclude_unset=True, exclude_none=True)
    user = await update_user(session, user_id, update_data)
    return success_response(user)
