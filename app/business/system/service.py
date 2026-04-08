from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import MenuModel
from app.core.exceptions import NotFoundException, ValidationException
from app.core.logger import logger


def menu_to_dict(menu: MenuModel) -> dict:
    return {
        "id": menu.id,
        "path": menu.path,
        "name": menu.name,
        "component": menu.component,
        "meta": menu.meta,
        "parentId": menu.parent_id,
        "order": menu.order,
        "createdAt": menu.created_at,
        "updatedAt": menu.updated_at,
    }


def build_menu_tree(menus: list[dict], parent_id: Optional[int] = None) -> list[dict]:
    tree = []
    current_level = [m for m in menus if m.get("parentId") == parent_id]
    current_level.sort(key=lambda x: (x.get("order") is None, x.get("order") or 9999))
    for menu in current_level:
        children = build_menu_tree(menus, menu["id"])
        if children:
            menu["children"] = children
        tree.append(menu)
    return tree


async def get_all_menus(session: AsyncSession) -> list[dict]:
    stmt = select(MenuModel).order_by(MenuModel.parent_id.asc(), MenuModel.order.asc())
    result = await session.execute(stmt)
    menus = result.scalars().all()
    menu_list = [menu_to_dict(m) for m in menus]
    return build_menu_tree(menu_list)


async def get_menu_by_id(session: AsyncSession, menu_id: int) -> Optional[dict]:
    menu = await session.get(MenuModel, menu_id)
    return menu_to_dict(menu) if menu else None


async def create_menu(session: AsyncSession, data: dict) -> dict:
    if data.get("order") is None:
        parent_id = data.get("parentId")
        stmt = select(func.max(MenuModel.order)).where(MenuModel.parent_id == parent_id)
        result = await session.execute(stmt)
        max_order = result.scalar() or 0
        data["order"] = max_order + 1
    menu = MenuModel(
        path=data.get("path"),
        name=data.get("name"),
        component=data.get("component"),
        meta=data.get("meta"),
        parent_id=data.get("parentId"),
        order=data.get("order"),
    )
    session.add(menu)
    await session.commit()
    await session.refresh(menu)
    return menu_to_dict(menu)


async def update_menu(session: AsyncSession, menu_id: int, data: dict) -> Optional[dict]:
    menu = await session.get(MenuModel, menu_id)
    if not menu:
        return None
    field_map = {"path": "path", "name": "name", "component": "component", "meta": "meta", "parentId": "parent_id", "order": "order"}
    for camel_key, snake_key in field_map.items():
        if camel_key in data and data[camel_key] is not None:
            setattr(menu, snake_key, data[camel_key])
    await session.commit()
    await session.refresh(menu)
    return menu_to_dict(menu)


async def delete_menu(session: AsyncSession, menu_id: int) -> bool:
    menu = await session.get(MenuModel, menu_id)
    if not menu:
        return False
    children_stmt = select(MenuModel).where(MenuModel.parent_id == menu_id)
    children_result = await session.execute(children_stmt)
    for child in children_result.scalars().all():
        await delete_menu(session, child.id)
    await session.delete(menu)
    await session.commit()
    return True
