from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    userName: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class RegisterRequest(BaseModel):
    userName: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    isActive: bool = Field(True, description="是否激活")
