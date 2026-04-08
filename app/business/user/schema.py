from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserUpdateRequest(BaseModel):
    userName: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    password: Optional[str] = Field(None, min_length=6, max_length=128, description="密码")
    isActive: Optional[bool] = Field(None, description="是否激活")


class UserResponse(BaseModel):
    id: int
    userName: str
    isActive: bool
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
