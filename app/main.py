import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.logger import setup_logger, logger, set_websocket_broadcast
from app.core.websocket_manager import manager
from app.core.exceptions import AppException, RequestValidationError
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from app.core.exceptions import (
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api import auth, user, nav, system, upload, proxy, transfer, openlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    await init_db()
    await init_redis()
    set_websocket_broadcast(manager.broadcast)
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"{settings.APP_NAME} 启动完成")
    yield
    await close_db()
    await close_redis()
    logger.info(f"{settings.APP_NAME} 已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(FastAPIRequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(nav.router)
app.include_router(system.router)
app.include_router(upload.router)
app.include_router(proxy.router)
app.include_router(transfer.router)
app.include_router(openlist.router)


static_dir = Path(settings.UPLOAD_DIR)
if static_dir.exists():
    app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=str(static_dir)), name="uploads")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    client_ip = request.client.host if request.client else "unknown"
    logger.bind(type="access").info(
        f"{client_ip} | {request.method} | {request.url.path} | {response.status_code} | {process_time:.2f}ms"
    )
    return response
