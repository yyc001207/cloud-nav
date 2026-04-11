from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IconInfo(BaseModel):
    type: str = Field(..., description="图标类型：file 或 text")
    url: Optional[str] = Field(None, description="文件 URL")
    text: Optional[str] = Field(None, description="显示文字")
    backgroundColor: Optional[str] = Field("#2ecc71", description="背景颜色")


class DocumentLink(BaseModel):
    title: str = Field(..., description="文档标题")
    url: str = Field(..., description="文档地址")


class TabCreateRequest(BaseModel):
    label: str = Field(..., description="标签名称")
    desc: Optional[str] = Field(None, description="描述")
    order: Optional[int] = Field(None, description="排序值")


class TabUpdateRequest(BaseModel):
    id: int = Field(..., description="Tab ID")
    label: Optional[str] = Field(None, description="标签名称")
    desc: Optional[str] = Field(None, description="描述")
    order: Optional[int] = Field(None, description="排序值")


class TabListRequest(BaseModel):
    pageNum: Optional[int] = Field(
        None, description="页码，从 1 开始，与 pageSize 同时传入时生效"
    )
    pageSize: Optional[int] = Field(
        None, description="每页数量，与 pageNum 同时传入时生效"
    )
    label: Optional[str] = Field(None, description="标签名称模糊查询")
    orderBy: Optional[str] = Field(
        None, description="排序字段：order、createdAt、updatedAt"
    )
    orderDir: Optional[str] = Field(None, description="排序方向：asc 或 desc")


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
    document: Optional[List[DocumentLink]] = Field(None, description="文档链接列表")
    tabId: int = Field(..., description="关联的 Tab ID")
    order: Optional[int] = Field(None, description="排序值")


class WebsiteUpdateRequest(BaseModel):
    id: int = Field(..., description="Website ID")
    label: Optional[str] = Field(None, description="网站名称")
    url: Optional[str] = Field(None, description="网站地址")
    desc: Optional[str] = Field(None, description="描述")
    icon: Optional[IconInfo] = Field(None, description="图标信息")
    document: Optional[List[DocumentLink]] = Field(None, description="文档链接列表")
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
    document: Optional[List[dict]] = None
    order: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class WebsiteOrderRequest(BaseModel):
    tabId: int = Field(..., description="标签页 ID")
    websiteIds: list[int] = Field(..., description="Website ID 数组")


class WebsiteListRequest(BaseModel):
    tabId: Optional[int] = Field(None, description="Tab ID")
    label: Optional[str] = Field(None, description="网站名称模糊查询")
    pageNum: Optional[int] = Field(
        None, description="页码，从 1 开始，与 pageSize 同时传入时生效"
    )
    pageSize: Optional[int] = Field(
        None, description="每页数量，与 pageNum 同时传入时生效"
    )
    orderBy: Optional[str] = Field(
        None, description="排序字段：order、label、createdAt、updatedAt"
    )
    orderDir: Optional[str] = Field(None, description="排序方向：asc 或 desc")
