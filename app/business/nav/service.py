from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import TabModel, WebsiteModel
from app.core.exceptions import NotFoundException, ValidationException
from app.core.logger import logger


def tab_to_dict(tab: TabModel) -> dict:
    return {
        "id": tab.id,
        "userId": tab.user_id,
        "label": tab.label,
        "desc": tab.desc,
        "order": tab.order,
        "createdAt": tab.created_at,
        "updatedAt": tab.updated_at,
    }


def website_to_dict(website: WebsiteModel) -> dict:
    return {
        "id": website.id,
        "userId": website.user_id,
        "tabId": website.tab_id,
        "label": website.label,
        "url": website.url,
        "desc": website.desc,
        "icon": website.icon,
        "github": website.github,
        "document": website.document,
        "order": website.order,
        "createdAt": website.created_at,
        "updatedAt": website.updated_at,
    }


async def get_all_tabs(session: AsyncSession, user_id: int) -> list[dict]:
    stmt = select(TabModel).where(TabModel.user_id == user_id).order_by(TabModel.order.asc(), TabModel.updated_at.desc())
    result = await session.execute(stmt)
    tabs = result.scalars().all()
    return [tab_to_dict(t) for t in tabs]


async def get_tab_by_id(session: AsyncSession, tab_id: int, user_id: int) -> Optional[dict]:
    stmt = select(TabModel).where(TabModel.id == tab_id, TabModel.user_id == user_id)
    result = await session.execute(stmt)
    tab = result.scalar_one_or_none()
    return tab_to_dict(tab) if tab else None


async def create_tab(session: AsyncSession, data: dict, user_id: int) -> dict:
    if data.get("order") is None:
        stmt = select(func.max(TabModel.order)).where(TabModel.user_id == user_id)
        result = await session.execute(stmt)
        max_order = result.scalar() or 0
        data["order"] = max_order + 1
    tab = TabModel(user_id=user_id, **data)
    session.add(tab)
    await session.commit()
    await session.refresh(tab)
    return tab_to_dict(tab)


async def update_tab(session: AsyncSession, tab_id: int, data: dict, user_id: int) -> Optional[dict]:
    stmt = select(TabModel).where(TabModel.id == tab_id, TabModel.user_id == user_id)
    result = await session.execute(stmt)
    tab = result.scalar_one_or_none()
    if not tab:
        return None
    for key, value in data.items():
        if value is not None and key != "id":
            setattr(tab, key, value)
    await session.commit()
    await session.refresh(tab)
    return tab_to_dict(tab)


async def delete_tab(session: AsyncSession, tab_id: int, user_id: int) -> bool:
    stmt = select(TabModel).where(TabModel.id == tab_id, TabModel.user_id == user_id)
    result = await session.execute(stmt)
    tab = result.scalar_one_or_none()
    if not tab:
        return False
    count_stmt = select(func.count()).where(WebsiteModel.tab_id == tab_id, WebsiteModel.user_id == user_id)
    count_result = await session.execute(count_stmt)
    if count_result.scalar() > 0:
        raise ValidationException("该标签下还有网站，请先清空后再删除")
    await session.delete(tab)
    await session.commit()
    return True


async def get_all_websites(session: AsyncSession, user_id: int, tab_id: Optional[int] = None, label: Optional[str] = None, page: int = 1, size: int = 0) -> tuple[list[dict], int]:
    conditions = [WebsiteModel.user_id == user_id]
    if tab_id:
        conditions.append(WebsiteModel.tab_id == tab_id)
    if label:
        conditions.append(WebsiteModel.label.like(f"%{label}%"))
    count_stmt = select(func.count()).where(*conditions)
    total = (await session.execute(count_stmt)).scalar() or 0
    stmt = select(WebsiteModel).where(*conditions).order_by(WebsiteModel.order.asc(), WebsiteModel.updated_at.desc())
    if size > 0:
        stmt = stmt.offset((page - 1) * size).limit(size)
    result = await session.execute(stmt)
    websites = result.scalars().all()
    return [website_to_dict(w) for w in websites], total


async def get_website_by_id(session: AsyncSession, website_id: int, user_id: int) -> Optional[dict]:
    stmt = select(WebsiteModel).where(WebsiteModel.id == website_id, WebsiteModel.user_id == user_id)
    result = await session.execute(stmt)
    website = result.scalar_one_or_none()
    return website_to_dict(website) if website else None


async def create_website(session: AsyncSession, data: dict, user_id: int) -> dict:
    if data.get("order") is None:
        tab_id = data.get("tabId")
        stmt = select(func.max(WebsiteModel.order)).where(WebsiteModel.tab_id == tab_id, WebsiteModel.user_id == user_id)
        result = await session.execute(stmt)
        max_order = result.scalar() or 0
        data["order"] = max_order + 1
    website = WebsiteModel(
        user_id=user_id,
        tab_id=data.get("tabId"),
        label=data.get("label"),
        url=data.get("url"),
        desc=data.get("desc"),
        icon=data.get("icon"),
        github=data.get("github"),
        document=data.get("document"),
        order=data.get("order"),
    )
    session.add(website)
    await session.commit()
    await session.refresh(website)
    return website_to_dict(website)


async def update_website(session: AsyncSession, website_id: int, data: dict, user_id: int) -> Optional[dict]:
    stmt = select(WebsiteModel).where(WebsiteModel.id == website_id, WebsiteModel.user_id == user_id)
    result = await session.execute(stmt)
    website = result.scalar_one_or_none()
    if not website:
        return None
    field_map = {"tabId": "tab_id", "label": "label", "url": "url", "desc": "desc", "icon": "icon", "github": "github", "document": "document", "order": "order"}
    for camel_key, snake_key in field_map.items():
        if camel_key in data and data[camel_key] is not None:
            setattr(website, snake_key, data[camel_key])
    await session.commit()
    await session.refresh(website)
    return website_to_dict(website)


async def delete_website(session: AsyncSession, website_id: int, user_id: int) -> bool:
    stmt = select(WebsiteModel).where(WebsiteModel.id == website_id, WebsiteModel.user_id == user_id)
    result = await session.execute(stmt)
    website = result.scalar_one_or_none()
    if not website:
        return False
    await session.delete(website)
    await session.commit()
    return True


async def batch_update_website_order(session: AsyncSession, tab_id: int, website_ids: list[int], user_id: int) -> bool:
    for index, website_id in enumerate(website_ids, start=1):
        stmt = update(WebsiteModel).where(WebsiteModel.id == website_id, WebsiteModel.user_id == user_id, WebsiteModel.tab_id == tab_id).values(order=index)
        await session.execute(stmt)
    await session.commit()
    return True
