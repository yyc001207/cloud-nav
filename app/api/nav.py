from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.nav.schema import (
    TabCreateRequest, TabUpdateRequest, WebsiteCreateRequest,
    WebsiteUpdateRequest, WebsiteOrderRequest, WebsiteListRequest,
)
from app.business.nav.service import (
    get_all_tabs, create_tab, update_tab, delete_tab,
    get_all_websites, create_website, update_website, delete_website,
    batch_update_website_order,
)
from app.utils.response import success_response, paginated_response
from app.core.exceptions import NotFoundException, ValidationException
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/nav", tags=["导航管理"])


@router.post("/tabs")
async def list_tabs(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    tabs = await get_all_tabs(session, user_id)
    return success_response(tabs)


@router.post("/tab/add")
async def add_tab(request: TabCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    tab = await create_tab(session, data, user_id)
    return success_response(tab)


@router.post("/tab/update")
async def update_tab_route(request: TabUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    tab = await update_tab(session, request.id, data, user_id)
    if not tab:
        raise NotFoundException("标签")
    return success_response(tab)


@router.post("/tab/delete")
async def delete_tab_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await delete_tab(session, id, user_id)
    if not success:
        raise NotFoundException("标签")
    return success_response(msg="删除成功")


@router.post("/websites")
async def list_websites(request: WebsiteListRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    websites, total = await get_all_websites(session, user_id, request.tabId, request.label, request.pageNum, request.pageSize)
    if request.pageSize > 0:
        return paginated_response(websites, total)
    return success_response(websites)


@router.post("/website/add")
async def add_website(request: WebsiteCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    website = await create_website(session, data, user_id)
    return success_response(website)


@router.post("/website/update")
async def update_website_route(request: WebsiteUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    website = await update_website(session, request.id, data, user_id)
    if not website:
        raise NotFoundException("网站")
    return success_response(website)


@router.post("/website/delete")
async def delete_website_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await delete_website(session, id, user_id)
    if not success:
        raise NotFoundException("网站")
    return success_response(msg="删除成功")


@router.post("/website/order")
async def update_website_order(request: WebsiteOrderRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    await batch_update_website_order(session, request.tabId, request.websiteIds, user_id)
    return success_response(msg="排序更新成功")
