from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class MenuMeta(BaseModel):
    title: str = Field(..., description="菜单标题")
    type: str = Field(default="menu", description="菜单类型")
    hidden: bool = Field(default=False, description="是否隐藏")
    isTop: bool = Field(default=False, description="是否置顶")


class MenuCreateRequest(BaseModel):
    path: Optional[str] = Field(None, description="路由路径")
    name: Optional[str] = Field(None, description="路由名称")
    component: Optional[str] = Field(None, description="组件路径")
    meta: MenuMeta = Field(..., description="菜单元数据")
    parentId: Optional[int] = Field(None, description="父级菜单 ID")
    order: Optional[int] = Field(None, description="排序值")

    @field_validator("component")
    @classmethod
    def validate_component(cls, v):
        if v is not None and v != "":
            if not v.startswith("/"):
                raise ValueError("component 必须以/开头")
            if not v.endswith(".vue"):
                raise ValueError("component 必须以.vue 结尾")
        return v


class MenuUpdateRequest(BaseModel):
    id: int = Field(..., description="Menu ID")
    path: Optional[str] = Field(None, description="路由路径")
    name: Optional[str] = Field(None, description="路由名称")
    component: Optional[str] = Field(None, description="组件路径")
    meta: Optional[MenuMeta] = Field(None, description="菜单元数据")
    parentId: Optional[int] = Field(None, description="父级菜单 ID")
    order: Optional[int] = Field(None, description="排序值")


class MenuResponse(BaseModel):
    id: int
    path: Optional[str] = None
    name: Optional[str] = None
    component: Optional[str] = None
    meta: Optional[dict] = None
    parentId: Optional[int] = None
    order: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    children: Optional[List["MenuResponse"]] = None
