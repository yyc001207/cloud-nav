from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.system.schema import MenuCreateRequest, MenuUpdateRequest
from app.business.system.service import get_all_menus, create_menu, update_menu, delete_menu
from app.utils.response import success_response
from app.core.exceptions import NotFoundException
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/system", tags=["系统管理"])


@router.post("/menus")
async def list_menus(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    await get_current_user_id(authorization)
    menus = await get_all_menus(session)
    return success_response(menus)


@router.post("/menu/add")
async def add_menu(request: MenuCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    menu = await create_menu(session, data)
    return success_response(menu)


@router.post("/menu/update")
async def update_menu_route(request: MenuUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    menu = await update_menu(session, request.id, data)
    if not menu:
        raise NotFoundException("菜单")
    return success_response(menu)


@router.post("/menu/delete")
async def delete_menu_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    await get_current_user_id(authorization)
    success = await delete_menu(session, id)
    if not success:
        raise NotFoundException("菜单")
    return success_response(msg="删除成功")
