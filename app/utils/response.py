from typing import Any, Optional


def success_response(data: Any = None, msg: str = "success") -> dict:
    return {"code": 200, "msg": msg, "data": data}


def error_response(msg: str = "error", code: int = 500, data: Any = None) -> dict:
    return {"code": code, "msg": msg, "data": data}


def paginated_response(data: list, total: int, msg: str = "success") -> dict:
    return {"code": 200, "msg": msg, "data": data, "total": total}


def login_success_response(token: str, msg: str = "登录成功") -> dict:
    return {"code": 200, "msg": msg, "token": token}
