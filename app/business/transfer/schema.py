from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TextTransferCreateRequest(BaseModel):
    content: str = Field(..., description="文本内容")
    title: Optional[str] = Field(None, description="文本标题")


class TextTransferUpdateRequest(BaseModel):
    id: int = Field(..., description="文本中转 ID")
    title: Optional[str] = Field(None, description="文本标题")


class TextTransferResponse(BaseModel):
    id: int
    content: str
    title: Optional[str] = None
    userId: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class FileTransferCreateRequest(BaseModel):
    filename: str = Field(..., description="文件名")
    fileSize: int = Field(..., description="文件大小")
    fileHash: str = Field(..., description="文件哈希值")
    contentType: str = Field(..., description="文件类型")


class FileTransferResponse(BaseModel):
    id: int
    filename: str
    fileSize: int
    fileHash: Optional[str] = None
    contentType: Optional[str] = None
    userId: Optional[int] = None
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class FileChunkRequest(BaseModel):
    fileId: int = Field(..., description="文件 ID")
    chunkIndex: int = Field(..., description="分片索引")
    totalChunks: int = Field(..., description="总分片数")


class FileCompleteRequest(BaseModel):
    fileId: int = Field(..., description="文件 ID")
    totalChunks: int = Field(..., description="总分片数")


class TransferListRequest(BaseModel):
    date: Optional[str] = Field(None, description="按日期查询，格式：YYYY-MM-DD")
    pageNum: Optional[int] = Field(
        None, description="页码，从 1 开始，与 pageSize 同时传入时生效"
    )
    pageSize: Optional[int] = Field(
        None, description="每页数量，与 pageNum 同时传入时生效"
    )
    keyword: Optional[str] = Field(None, description="关键词模糊查询")
    status: Optional[str] = Field(None, description="文件状态过滤：pending、completed")
    orderBy: Optional[str] = Field(None, description="排序字段：createdAt、updatedAt、fileSize")
    orderDir: Optional[str] = Field(None, description="排序方向：asc 或 desc")
