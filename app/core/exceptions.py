from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logger import logger


class AppException(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, resource: str = "资源"):
        super().__init__(f"{resource}不存在", code=404)


class ValidationException(AppException):
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(message, code=400)


class AuthException(AppException):
    def __init__(self, message: str = "未授权或登录失效"):
        super().__init__(message, code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "msg": exc.message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    msg = "; ".join([f"{e.get('loc', [])[-1]}: {e.get('msg', '')}" for e in errors])
    return JSONResponse(
        status_code=400,
        content={"code": 400, "msg": f"请求参数错误: {msg}"},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "msg": "服务器内部错误"},
    )
