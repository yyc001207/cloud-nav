import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


_strm_handler_added = False
_websocket_broadcast = None


def setup_logger() -> None:
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    logger.add(
        str(log_dir / "access.log"),
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: record["extra"].get("type") == "access",
    )

    logger.add(
        str(log_dir / "error.log"),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )


def set_websocket_broadcast(broadcast_func):
    global _websocket_broadcast
    _websocket_broadcast = broadcast_func


def _ws_sink(message):
    record = message.record
    log_data = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "level": record["level"].name,
        "message": record["message"],
        "name": record.get("extra", {}).get("name", ""),
    }
    if _websocket_broadcast and record.get("extra", {}).get("name") == "strm_generator":
        import asyncio
        try:
            asyncio.create_task(_websocket_broadcast(log_data))
        except Exception:
            pass


def get_strm_logger():
    global _strm_handler_added
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    if not _strm_handler_added:
        import logging

        logger.add(
            str(log_dir / "alist_strm.log"),
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            rotation="50 MB",
            retention="10 days",
            compression="zip",
            filter=lambda record: record["extra"].get("name") == "strm_generator",
        )

        logger.add(
            str(log_dir / "alist_strm_error.log"),
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: record["extra"].get("name") == "strm_generator" and record["level"].no >= logging.ERROR,
        )

        logger.add(
            _ws_sink,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            filter=lambda record: record["extra"].get("name") == "strm_generator",
        )

        _strm_handler_added = True

    return logger.bind(name="strm_generator")
