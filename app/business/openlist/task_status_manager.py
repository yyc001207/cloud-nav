import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
from app.core.logger import logger


class TaskStatusManager:
    _running_tasks: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_task(cls, task_id: str, task: asyncio.Task) -> None:
        cls._running_tasks[task_id] = {"task": task, "cancelled": False, "start_time": datetime.utcnow()}
        logger.info(f"任务 {task_id} 已注册")

    @classmethod
    def unregister_task(cls, task_id: str) -> None:
        if task_id in cls._running_tasks:
            del cls._running_tasks[task_id]
            logger.info(f"任务 {task_id} 已注销")

    @classmethod
    def is_task_running(cls, task_id: str) -> bool:
        if task_id not in cls._running_tasks:
            return False
        task_info = cls._running_tasks[task_id]
        return not task_info["task"].done() and not task_info["cancelled"]

    @classmethod
    def is_cancelled(cls, task_id: str) -> bool:
        if task_id in cls._running_tasks:
            return cls._running_tasks[task_id]["cancelled"]
        return False

    @classmethod
    async def cancel_task(cls, task_id: str) -> bool:
        if task_id not in cls._running_tasks:
            return False
        task_info = cls._running_tasks[task_id]
        task = task_info["task"]
        if task.done():
            cls.unregister_task(task_id)
            return False
        task_info["cancelled"] = True
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"任务 {task_id} 已取消")
        cls.unregister_task(task_id)
        return True

    @classmethod
    def get_running_tasks(cls) -> Dict[str, Dict[str, Any]]:
        result = {}
        for task_id, info in cls._running_tasks.items():
            if not info["task"].done():
                result[task_id] = {"task_id": task_id, "start_time": info["start_time"], "cancelled": info["cancelled"]}
        return result
