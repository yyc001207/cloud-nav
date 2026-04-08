from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str = Field(..., description="文件名")
    url: str = Field(..., description="文件 URL")
    size: int = Field(..., description="文件大小（字节）")
