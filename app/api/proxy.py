from fastapi import APIRouter, Depends, Header
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.proxy.schema import (
    WeatherRequest,
    HolidayCreateRequest,
    HolidayListRequest,
    HolidayQueryRequest,
)
from app.business.proxy.service import (
    get_full_weather,
    get_all_holidays,
    get_holiday_by_year,
    create_or_update_holiday,
    delete_holiday,
)
from app.utils.response import success_response, paginated_response
from app.core.exceptions import NotFoundException
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/proxy", tags=["代理服务"])


@router.post("/weather")
async def get_weather(
    request: WeatherRequest, authorization: Optional[str] = Header(None)
):
    await get_current_user_id(authorization)
    weather = await get_full_weather(request.location)
    return success_response(weather)


@router.post("/holidays")
async def list_holidays(
    request: HolidayListRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    await get_current_user_id(authorization)
    holidays, total = await get_all_holidays(
        session,
        year=request.year,
        page=request.pageNum,
        size=request.pageSize,
        order_by=request.orderBy,
        order_dir=request.orderDir or "asc",
    )
    if request.pageNum is not None and request.pageSize is not None:
        return paginated_response(holidays, total)
    return success_response(holidays)


@router.post("/holiday/query")
async def query_holiday(
    request: HolidayQueryRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    await get_current_user_id(authorization)
    holiday = await get_holiday_by_year(session, request.year)
    return success_response(holiday)


@router.post("/holiday/add")
async def add_holiday(
    request: HolidayCreateRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    await get_current_user_id(authorization)
    holiday = await create_or_update_holiday(session, request.year)
    return success_response(holiday)


@router.post("/holiday/delete")
async def delete_holiday_route(
    id: int,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    await get_current_user_id(authorization)
    success = await delete_holiday(session, id)
    if not success:
        raise NotFoundException("节假日数据")
    return success_response(msg="删除成功")
