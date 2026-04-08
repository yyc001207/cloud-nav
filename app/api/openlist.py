import asyncio
import uuid
from fastapi import APIRouter, Depends, Header, WebSocket, WebSocketDisconnect
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.business.openlist.schema import (
    OpenListGlobalConfigCreateRequest, OpenListGlobalConfigUpdateRequest,
    OpenListTaskConfigCreateRequest, OpenListTaskConfigUpdateRequest,
    OpenListExecuteRequest,
)
from app.business.openlist.service import (
    create_global_config, get_global_config, update_global_config, delete_global_config,
    create_task_config, get_task_config, update_task_config, delete_task_config,
    list_task_configs, add_execution_record, get_global_config_by_id, get_task_config_by_id,
)
from app.business.openlist.strm_generator import STRMGenerator
from app.business.openlist.task_status_manager import TaskStatusManager
from app.core.websocket_manager import manager
from app.core.logger import logger, set_websocket_broadcast
from app.utils.response import success_response
from app.core.exceptions import NotFoundException, ValidationException
from app.api.user import get_current_user_id

router = APIRouter(prefix="/api/openlist", tags=["OpenList STRM"])


@router.post("/global-config")
async def get_global_config_route(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    config = await get_global_config(session, user_id)
    return success_response(config)


@router.post("/global-config/add")
async def add_global_config(request: OpenListGlobalConfigCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    config = await create_global_config(session, user_id, data)
    return success_response(config)


@router.post("/global-config/update")
async def update_global_config_route(request: OpenListGlobalConfigUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    config = await update_global_config(session, user_id, data)
    return success_response(config)


@router.post("/global-config/delete")
async def delete_global_config_route(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await delete_global_config(session, user_id)
    if not success:
        raise NotFoundException("全局配置")
    return success_response(msg="删除成功")


@router.post("/task-config/list")
async def list_task_configs_route(authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    configs = await list_task_configs(session, user_id)
    return success_response(configs)


@router.post("/task-config")
async def get_task_config_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    config = await get_task_config(session, user_id, id)
    if not config:
        raise NotFoundException("任务配置")
    return success_response(config)


@router.post("/task-config/add")
async def add_task_config(request: OpenListTaskConfigCreateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    config = await create_task_config(session, user_id, data)
    return success_response(config)


@router.post("/task-config/update")
async def update_task_config_route(id: int, request: OpenListTaskConfigUpdateRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    data = request.model_dump(exclude_unset=True, exclude_none=True)
    config = await update_task_config(session, user_id, id, data)
    return success_response(config)


@router.post("/task-config/delete")
async def delete_task_config_route(id: int, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    success = await delete_task_config(session, user_id, id)
    if not success:
        raise NotFoundException("任务配置")
    return success_response(msg="删除成功")


@router.post("/execute")
async def execute_strm_task(request: OpenListExecuteRequest, authorization: Optional[str] = Header(None), session: AsyncSession = Depends(get_session)):
    user_id = await get_current_user_id(authorization)
    global_config = await get_global_config_by_id(session, request.globalConfigId, user_id)
    if not global_config:
        raise NotFoundException("全局配置")
    task_config = await get_task_config_by_id(session, request.taskConfigId, user_id)
    if not task_config:
        raise NotFoundException("任务配置")
    task_id = str(uuid.uuid4())
    generator = STRMGenerator(global_config, task_config, task_id)

    async def run_task():
        try:
            stats = await generator.execute(force=request.force)
            await add_execution_record(
                session, user_id, request.taskConfigId,
                success=True, message="执行完成", **stats,
            )
        except asyncio.CancelledError:
            await add_execution_record(
                session, user_id, request.taskConfigId,
                success=False, message="任务已取消",
            )
        except Exception as e:
            logger.error(f"STRM 任务执行失败: {e}")
            await add_execution_record(
                session, user_id, request.taskConfigId,
                success=False, message=str(e),
            )
        finally:
            TaskStatusManager.unregister_task(task_id)

    task = asyncio.create_task(run_task())
    TaskStatusManager.register_task(task_id, task)
    return success_response({"taskId": task_id, "message": "任务已开始执行"})


@router.post("/cancel")
async def cancel_strm_task(taskId: str, authorization: Optional[str] = Header(None)):
    await get_current_user_id(authorization)
    success = await TaskStatusManager.cancel_task(taskId)
    return success_response(msg="任务已取消" if success else "取消失败")


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket, "all")
    set_websocket_broadcast(manager.broadcast)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "all")
