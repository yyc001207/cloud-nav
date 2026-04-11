from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class OpenListGlobalConfigCreateRequest(BaseModel):
    baseUrl: str = Field(..., description="OpenList 服务器地址")
    token: str = Field(..., description="OpenList Token")
    videoExtensions: Optional[List[str]] = Field(
        default=[".mp4", ".mkv", ".avi", ".wmv", ".flv", ".mov", ".webm"],
        description="视频格式",
    )
    subtitleExtensions: Optional[List[str]] = Field(
        default=[".srt", ".ass", ".ssa", ".sub", ".vtt"], description="字幕格式"
    )


class OpenListGlobalConfigUpdateRequest(BaseModel):
    baseUrl: Optional[str] = None
    token: Optional[str] = None
    videoExtensions: Optional[List[str]] = None
    subtitleExtensions: Optional[List[str]] = None


class OpenListTaskConfigCreateRequest(BaseModel):
    name: str = Field(..., description="任务配置名称")
    outputDir: Optional[str] = Field(None, description="输出目录")
    taskPaths: str = Field(..., description="处理路径")
    maxScanDepth: Optional[int] = Field(None, description="扫描深度限制")


class OpenListTaskConfigUpdateRequest(BaseModel):
    name: Optional[str] = None
    outputDir: Optional[str] = None
    taskPaths: Optional[str] = None
    maxScanDepth: Optional[int] = None


class TaskConfigListRequest(BaseModel):
    pageNum: Optional[int] = Field(
        None, description="页码，从 1 开始，与 pageSize 同时传入时生效"
    )
    pageSize: Optional[int] = Field(
        None, description="每页数量，与 pageNum 同时传入时生效"
    )
    name: Optional[str] = Field(None, description="任务配置名称模糊查询")
    orderBy: Optional[str] = Field(
        None, description="排序字段：createdAt、updatedAt、name"
    )
    orderDir: Optional[str] = Field(None, description="排序方向：asc 或 desc")


class OpenListGlobalConfigResponse(BaseModel):
    id: int
    userId: int
    baseUrl: str
    videoExtensions: Optional[List[str]] = None
    subtitleExtensions: Optional[List[str]] = None
    tokenMasked: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class OpenListTaskConfigResponse(BaseModel):
    id: int
    userId: int
    name: str
    outputDir: Optional[str] = None
    taskPaths: str
    maxScanDepth: Optional[int] = None
    executionHistory: Optional[List[Dict[str, Any]]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class OpenListExecuteRequest(BaseModel):
    globalConfigId: int = Field(..., description="全局配置 ID")
    taskConfigId: int = Field(..., description="任务配置 ID")
    incrementalMode: bool = Field(True, description="是否增量更新")
    force: bool = Field(False, description="是否强制重新生成")


class TaskStats(BaseModel):
    totalVideos: int = 0
    successVideos: int = 0
    errorVideos: int = 0
    totalSubtitles: int = 0
    successSubtitles: int = 0
    errorSubtitles: int = 0


class TaskHistoryRequest(BaseModel):
    taskConfigId: int = Field(..., description="任务配置 ID")
