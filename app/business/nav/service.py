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
        "document": website.document,
        "order": website.order,
        "createdAt": website.created_at,
        "updatedAt": website.updated_at,
    }


TAB_ORDER_FIELDS = {
    "order": TabModel.order,
    "createdAt": TabModel.created_at,
    "updatedAt": TabModel.updated_at,
}


async def get_all_tabs(
    session: AsyncSession,
    user_id: int,
    page: Optional[int] = None,
    size: Optional[int] = None,
    label: Optional[str] = None,
    order_by: Optional[str] = None,
    order_dir: Optional[str] = "asc",
) -> tuple[list[dict], int]:
    conditions = [TabModel.user_id == user_id]
    if label:
        conditions.append(TabModel.label.like(f"%{label}%"))
    count_stmt = select(func.count()).where(*conditions)
    total = (await session.execute(count_stmt)).scalar() or 0
    stmt = select(TabModel).where(*conditions)
    order_column = TAB_ORDER_FIELDS.get(order_by) if order_by else None
    if order_column is not None:
        stmt = stmt.order_by(
            order_column.desc() if order_dir == "desc" else order_column.asc()
        )
    else:
        stmt = stmt.order_by(TabModel.order.asc(), TabModel.updated_at.desc())
    if page is not None and size is not None and size > 0:
        stmt = stmt.offset((page - 1) * size).limit(size)
    result = await session.execute(stmt)
    tabs = result.scalars().all()
    return [tab_to_dict(t) for t in tabs], total


async def get_tab_by_id(
    session: AsyncSession, tab_id: int, user_id: int
) -> Optional[dict]:
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


async def update_tab(
    session: AsyncSession, tab_id: int, data: dict, user_id: int
) -> Optional[dict]:
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
    count_stmt = select(func.count()).where(
        WebsiteModel.tab_id == tab_id, WebsiteModel.user_id == user_id
    )
    count_result = await session.execute(count_stmt)
    if count_result.scalar() > 0:
        raise ValidationException("该标签下还有网站，请先清空后再删除")
    await session.delete(tab)
    await session.commit()
    return True


WEBSITE_ORDER_FIELDS = {
    "order": WebsiteModel.order,
    "label": WebsiteModel.label,
    "createdAt": WebsiteModel.created_at,
    "updatedAt": WebsiteModel.updated_at,
}


async def get_all_websites(
    session: AsyncSession,
    user_id: int,
    tab_id: Optional[int] = None,
    label: Optional[str] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    order_by: Optional[str] = None,
    order_dir: Optional[str] = "asc",
) -> tuple[list[dict], int]:
    conditions = [WebsiteModel.user_id == user_id]
    if tab_id:
        conditions.append(WebsiteModel.tab_id == tab_id)
    if label:
        conditions.append(WebsiteModel.label.like(f"%{label}%"))
    count_stmt = select(func.count()).where(*conditions)
    total = (await session.execute(count_stmt)).scalar() or 0
    stmt = select(WebsiteModel).where(*conditions)
    order_column = WEBSITE_ORDER_FIELDS.get(order_by) if order_by else None
    if order_column is not None:
        stmt = stmt.order_by(
            order_column.desc() if order_dir == "desc" else order_column.asc()
        )
    else:
        stmt = stmt.order_by(WebsiteModel.order.asc(), WebsiteModel.updated_at.desc())
    if page is not None and size is not None and size > 0:
        stmt = stmt.offset((page - 1) * size).limit(size)
    result = await session.execute(stmt)
    websites = result.scalars().all()
    return [website_to_dict(w) for w in websites], total


async def get_website_by_id(
    session: AsyncSession, website_id: int, user_id: int
) -> Optional[dict]:
    stmt = select(WebsiteModel).where(
        WebsiteModel.id == website_id, WebsiteModel.user_id == user_id
    )
    result = await session.execute(stmt)
    website = result.scalar_one_or_none()
    return website_to_dict(website) if website else None


async def create_website(session: AsyncSession, data: dict, user_id: int) -> dict:
    if data.get("order") is None:
        tab_id = data.get("tabId")
        stmt = select(func.max(WebsiteModel.order)).where(
            WebsiteModel.tab_id == tab_id, WebsiteModel.user_id == user_id
        )
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
        document=data.get("document"),
        order=data.get("order"),
    )
    session.add(website)
    await session.commit()
    await session.refresh(website)
    return website_to_dict(website)


async def update_website(
    session: AsyncSession, website_id: int, data: dict, user_id: int
) -> Optional[dict]:
    stmt = select(WebsiteModel).where(
        WebsiteModel.id == website_id, WebsiteModel.user_id == user_id
    )
    result = await session.execute(stmt)
    website = result.scalar_one_or_none()
    if not website:
        return None
    field_map = {
        "tabId": "tab_id",
        "label": "label",
        "url": "url",
        "desc": "desc",
        "icon": "icon",
        "document": "document",
        "order": "order",
    }
    for camel_key, snake_key in field_map.items():
        if camel_key in data and data[camel_key] is not None:
            setattr(website, snake_key, data[camel_key])
    await session.commit()
    await session.refresh(website)
    return website_to_dict(website)


async def delete_website(session: AsyncSession, website_id: int, user_id: int) -> bool:
    stmt = select(WebsiteModel).where(
        WebsiteModel.id == website_id, WebsiteModel.user_id == user_id
    )
    result = await session.execute(stmt)
    website = result.scalar_one_or_none()
    if not website:
        return False
    await session.delete(website)
    await session.commit()
    return True


async def batch_update_website_order(
    session: AsyncSession, tab_id: int, website_ids: list[int], user_id: int
) -> bool:
    for index, website_id in enumerate(website_ids, start=1):
        stmt = (
            update(WebsiteModel)
            .where(
                WebsiteModel.id == website_id,
                WebsiteModel.user_id == user_id,
                WebsiteModel.tab_id == tab_id,
            )
            .values(order=index)
        )
        await session.execute(stmt)
    await session.commit()
    return True
