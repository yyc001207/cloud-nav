from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IconInfo(BaseModel):
    type: str = Field(..., description="图标类型：file 或 text")
    url: Optional[str] = Field(None, description="文件 URL")
    text: Optional[str] = Field(None, description="显示文字")
    backgroundColor: Optional[str] = Field("#2ecc71", description="背景颜色")


class TabCreateRequest(BaseModel):
    label: str = Field(..., description="标签名称")
    desc: Optional[str] = Field(None, description="描述")
    order: Optional[int] = Field(None, description="排序值")


class TabUpdateRequest(BaseModel):
    id: int = Field(..., description="Tab ID")
    label: Optional[str] = Field(None, description="标签名称")
    desc: Optional[str] = Field(None, description="描述")
    order: Optional[int] = Field(None, description="排序值")


class TabResponse(BaseModel):
    id: int
    userId: Optional[int] = None
    label: str
    desc: Optional[str] = None
    order: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class WebsiteCreateRequest(BaseModel):
    label: str = Field(..., description="网站名称")
    url: str = Field(..., description="网站地址")
    desc: Optional[str] = Field(None, description="描述")
    icon: Optional[IconInfo] = Field(None, description="图标信息")
    github: Optional[str] = Field(None, description="GitHub 地址")
    document: Optional[str] = Field(None, description="文档地址")
    tabId: int = Field(..., description="关联的 Tab ID")
    order: Optional[int] = Field(None, description="排序值")


class WebsiteUpdateRequest(BaseModel):
    id: int = Field(..., description="Website ID")
    label: Optional[str] = Field(None, description="网站名称")
    url: Optional[str] = Field(None, description="网站地址")
    desc: Optional[str] = Field(None, description="描述")
    icon: Optional[IconInfo] = Field(None, description="图标信息")
    github: Optional[str] = Field(None, description="GitHub 地址")
    document: Optional[str] = Field(None, description="文档地址")
    tabId: Optional[int] = Field(None, description="关联的 Tab ID")
    order: Optional[int] = Field(None, description="排序值")


class WebsiteResponse(BaseModel):
    id: int
    userId: Optional[int] = None
    tabId: Optional[int] = None
    label: str
    url: str
    desc: Optional[str] = None
    icon: Optional[dict] = None
    github: Optional[str] = None
    document: Optional[str] = None
    order: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class WebsiteOrderRequest(BaseModel):
    tabId: int = Field(..., description="标签页 ID")
    websiteIds: list[int] = Field(..., description="Website ID 数组")


class WebsiteListRequest(BaseModel):
    tabId: Optional[int] = Field(None, description="Tab ID")
    label: Optional[str] = Field(None, description="网站名称模糊查询")
    pageNum: int = Field(1, description="页码")
    pageSize: int = Field(0, description="每页数量，0 表示返回所有")
