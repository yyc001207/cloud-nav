from typing import Optional
import asyncio
import httpx
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import HolidayModel
from app.core.config import settings
from app.core.redis import cache_get_json, cache_set_json
from app.core.exceptions import NotFoundException, ValidationException
from app.core.logger import logger


def holiday_to_dict(holiday: HolidayModel) -> dict:
    return {
        "id": holiday.id,
        "year": holiday.year,
        "holiday": holiday.holiday,
        "adjustment": holiday.adjustment,
        "createdAt": holiday.created_at,
        "updatedAt": holiday.updated_at,
    }


async def get_city_location(location: str) -> Optional[list[dict]]:
    cache_key = f"weather:city:{location}"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    url = f"{settings.QWEATHER_HOST}/geo/v2/city/lookup"
    headers = {"X-QW-Api-Key": settings.QWEATHER_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, params={"location": location}, headers=headers, timeout=10.0
        )
        data = response.json()
    if data.get("code") == "200":
        result = data.get("location", [])
        await cache_set_json(cache_key, result, ttl=3600)
        return result
    return None


async def get_weather_now(location_id: str) -> Optional[dict]:
    cache_key = f"weather:now:{location_id}"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    url = f"{settings.QWEATHER_HOST}/v7/weather/now"
    headers = {"X-QW-Api-Key": settings.QWEATHER_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, params={"location": location_id}, headers=headers, timeout=10.0
        )
        data = response.json()
    if data.get("code") == "200":
        result = data.get("now", {})
        await cache_set_json(cache_key, result, ttl=300)
        return result
    return None


async def get_weather_hourly(location_id: str) -> list[dict]:
    cache_key = f"weather:hourly:{location_id}"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    url = f"{settings.QWEATHER_HOST}/v7/weather/24h"
    headers = {"X-QW-Api-Key": settings.QWEATHER_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, params={"location": location_id}, headers=headers, timeout=10.0
        )
        data = response.json()
    if data.get("code") == "200":
        result = data.get("hourly", [])
        await cache_set_json(cache_key, result, ttl=300)
        return result
    return []


async def get_weather_daily(location_id: str) -> list[dict]:
    cache_key = f"weather:daily:{location_id}"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    url = f"{settings.QWEATHER_HOST}/v7/weather/7d"
    headers = {"X-QW-Api-Key": settings.QWEATHER_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, params={"location": location_id}, headers=headers, timeout=10.0
        )
        data = response.json()
    if data.get("code") == "200":
        result = data.get("daily", [])
        await cache_set_json(cache_key, result, ttl=300)
        return result
    return []


async def get_air_quality(longitude: float, latitude: float) -> Optional[dict]:
    cache_key = f"weather:air:{longitude}:{latitude}"
    cached = await cache_get_json(cache_key)
    if cached:
        return cached
    url = (
        f"{settings.QWEATHER_HOST}/airquality/v1/current/{latitude:.2f}/{longitude:.2f}"
    )
    headers = {"X-QW-Api-Key": settings.QWEATHER_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10.0)
        data = response.json()
    if "indexes" in data or "pollutants" in data:
        await cache_set_json(cache_key, data, ttl=300)
        return data
    return None


async def get_full_weather(location: str) -> dict:
    if "," in location:
        parts = location.split(",")
        longitude, latitude = float(parts[0]), float(parts[1])
        city_info = await get_city_location(f"{longitude},{latitude}")
    elif location.isdigit():
        city_info = await get_city_location(location)
        longitude, latitude = 116.4074, 39.9042
    else:
        city_info = await get_city_location(location)
        longitude, latitude = 116.4074, 39.9042
    if not city_info or len(city_info) == 0:
        raise NotFoundException("地点")
    location_id = city_info[0].get("id")
    location_data = city_info[0]
    now, hourly, daily, air = await asyncio.gather(
        get_weather_now(location_id),
        get_weather_hourly(location_id),
        get_weather_daily(location_id),
        get_air_quality(longitude, latitude),
        return_exceptions=True,
    )
    return {
        "location": {
            "id": location_data.get("id", ""),
            "name": location_data.get("name", ""),
            "lat": location_data.get("lat", ""),
            "lon": location_data.get("lon", ""),
            "adm1": location_data.get("adm1", ""),
            "adm2": location_data.get("adm2", ""),
        },
        "now": now if not isinstance(now, Exception) else {},
        "hourly": hourly if not isinstance(hourly, Exception) else [],
        "daily": daily if not isinstance(daily, Exception) else [],
        "air": air if not isinstance(air, Exception) else {},
    }


async def fetch_holiday_from_api(year: int) -> Optional[dict]:
    url = f"{settings.HOLIDAY_API_BASE}/{year}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        data = response.json()
    holiday_data = data.get("holiday", {})
    holiday_dates = []
    adjustment_dates = []
    for date_key, day_info in holiday_data.items():
        date_str = day_info.get("date", "")
        if date_str:
            if day_info.get("holiday", False):
                holiday_dates.append(date_str)
            else:
                adjustment_dates.append(date_str)
    holiday_dates.sort()
    adjustment_dates.sort()
    return {
        "year": year,
        "holiday": ",".join(holiday_dates),
        "adjustment": ",".join(adjustment_dates),
    }


HOLIDAY_ORDER_FIELDS = {
    "year": HolidayModel.year,
    "createdAt": HolidayModel.created_at,
    "updatedAt": HolidayModel.updated_at,
}


async def get_all_holidays(
    session: AsyncSession,
    year: Optional[int] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    order_by: Optional[str] = None,
    order_dir: str = "asc",
) -> tuple[list[dict], int]:
    stmt = select(HolidayModel)
    count_stmt = select(sa_func.count()).select_from(HolidayModel)
    if year is not None:
        stmt = stmt.where(HolidayModel.year == year)
        count_stmt = count_stmt.where(HolidayModel.year == year)
    order_column = HOLIDAY_ORDER_FIELDS.get(order_by) if order_by else None
    if order_column is not None:
        stmt = stmt.order_by(
            order_column.desc() if order_dir == "desc" else order_column.asc()
        )
    else:
        stmt = stmt.order_by(HolidayModel.year.asc())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()
    if page is not None and size is not None and size > 0:
        stmt = stmt.offset((page - 1) * size).limit(size)
    result = await session.execute(stmt)
    holidays = result.scalars().all()
    return [holiday_to_dict(h) for h in holidays], total


async def get_holiday_by_year(session: AsyncSession, year: int) -> Optional[dict]:
    stmt = select(HolidayModel).where(HolidayModel.year == year)
    result = await session.execute(stmt)
    holiday = result.scalar_one_or_none()
    return holiday_to_dict(holiday) if holiday else None


async def create_or_update_holiday(session: AsyncSession, year: int) -> dict:
    api_data = await fetch_holiday_from_api(year)
    if not api_data:
        raise ValidationException("无法获取节假日数据")
    existing = await get_holiday_by_year(session, year)
    if existing:
        stmt = select(HolidayModel).where(HolidayModel.year == year)
        result = await session.execute(stmt)
        holiday = result.scalar_one()
        holiday.holiday = api_data["holiday"]
        holiday.adjustment = api_data["adjustment"]
        await session.commit()
        await session.refresh(holiday)
        return holiday_to_dict(holiday)
    holiday = HolidayModel(
        year=year, holiday=api_data["holiday"], adjustment=api_data["adjustment"]
    )
    session.add(holiday)
    await session.commit()
    await session.refresh(holiday)
    return holiday_to_dict(holiday)


async def delete_holiday(session: AsyncSession, holiday_id: int) -> bool:
    holiday = await session.get(HolidayModel, holiday_id)
    if not holiday:
        return False
    await session.delete(holiday)
    await session.commit()
    return True
