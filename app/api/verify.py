from fastapi import APIRouter, Request, Response
from app.utils.security import verify_token
from app.utils.response import success_response, error_response
from app.core.exceptions import AuthException

router = APIRouter(prefix="/api/verify", tags=["验证"])


@router.get("/token")
async def verify_user_token(request: Request, response: Response, token: str = None):
    token_value = token or request.cookies.get("token")
    if not token_value:
        response.status_code = 401
        return error_response(msg="Token无效", code=401)

    try:
        payload = await verify_token(token_value)
        user_name = payload.get("sub")
        return success_response(data={"valid": True, "username": user_name})
    except AuthException:
        response.status_code = 401
        return error_response(msg="Token无效", code=401)
