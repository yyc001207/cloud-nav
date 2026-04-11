from pydantic import BaseModel, Field
from typing import Optional


class WeatherRequest(BaseModel):
    location: str = Field(..., description="地点名称或 ID")


class HolidayCreateRequest(BaseModel):
    year: int = Field(..., description="年份")


class HolidayUpdateRequest(BaseModel):
    id: int = Field(..., description="Holiday ID")
    year: Optional[int] = Field(None, description="年份")
    holiday: Optional[str] = Field(None, description="节假日日期字符串")
    adjustment: Optional[str] = Field(None, description="调休日期字符串")


class HolidayResponse(BaseModel):
    id: int
    year: int
    holiday: Optional[str] = None
    adjustment: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class HolidayListRequest(BaseModel):
    year: Optional[int] = Field(None, description="按年份过滤")
    pageNum: Optional[int] = Field(
        None, description="页码，从 1 开始，与 pageSize 同时传入时生效"
    )
    pageSize: Optional[int] = Field(
        None, description="每页数量，与 pageNum 同时传入时生效"
    )
    orderBy: Optional[str] = Field(
        None, description="排序字段：year、createdAt、updatedAt"
    )
    orderDir: Optional[str] = Field(None, description="排序方向：asc 或 desc")


class HolidayQueryRequest(BaseModel):
    year: int = Field(..., description="年份")
