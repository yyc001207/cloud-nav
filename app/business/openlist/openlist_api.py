import asyncio
import httpx
from typing import Dict, List, Any
from urllib.parse import quote
from app.core.logger import logger, get_strm_logger


class OpenListAPI:
    _strm_logger = None

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {"Authorization": self.token, "Content-Type": "application/json"}
        if OpenListAPI._strm_logger is None:
            OpenListAPI._strm_logger = get_strm_logger()

    def _log(self, level: str, message: str):
        log_func = getattr(logger, level, logger.info)
        strm_log_func = getattr(OpenListAPI._strm_logger, level, OpenListAPI._strm_logger.info)
        log_func(message)
        strm_log_func(message)

    async def list_files(self, path: str = "/", page: int = 1, per_page: int = 0, password: str = "", refresh: bool = False, max_retries: int = 3) -> Dict[str, Any]:
        url = f"{self.base_url}/api/fs/list"
        data = {"path": path, "password": password, "page": page, "per_page": per_page, "refresh": refresh}
        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=data, headers=self.headers, timeout=30.0)
                    response.raise_for_status()
                    result = response.json()
                    if result.get("code") == 200:
                        return result["data"]
                    error_msg = result.get("message", "未知错误")
                    if "not found" in error_msg.lower():
                        self._log("warning", f"目录不存在: {path}")
                        raise Exception(f"API 调用失败：{error_msg}")
                    self._log("warning", f"OpenList API 调用失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")
                    last_error = Exception(f"API 调用失败：{error_msg}")
            except httpx.TimeoutException:
                self._log("warning", f"OpenList API 请求超时 (尝试 {attempt + 1}/{max_retries}): {path}")
                last_error = Exception("API 请求超时")
            except httpx.RequestError as e:
                self._log("warning", f"OpenList API 请求失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                last_error = Exception(f"API 请求失败：{str(e)}")
            except Exception as e:
                if "not found" in str(e).lower():
                    raise
                self._log("warning", f"OpenList API 错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                last_error = e
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
        self._log("error", f"OpenList API 重试 {max_retries} 次后仍失败: {path}")
        raise last_error

    async def get_file_info(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/fs/get"
        data = {"path": path}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                if result.get("code") == 200:
                    return result["data"]
                raise Exception(f"API 调用失败：{result.get('message', '未知错误')}")
        except httpx.TimeoutException:
            raise Exception("API 请求超时")
        except httpx.RequestError as e:
            raise Exception(f"API 请求失败：{str(e)}")

    async def download_file(self, file_path: str, save_path: str, max_retries: int = 5, encode: bool = True) -> bool:
        encoded_path = quote(file_path, safe="/") if encode else file_path
        download_url = f"{self.base_url}/d{encoded_path}"
        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    async with client.stream("GET", download_url, timeout=60.0) as response:
                        response.raise_for_status()
                        with open(save_path, "wb") as f:
                            async for chunk in response.aiter_bytes(chunk_size=8192):
                                f.write(chunk)
                        return True
            except Exception as e:
                last_error = e
                self._log("warning", f"文件下载失败 (尝试 {attempt + 1}/{max_retries}) {file_path}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
        self._log("error", f"文件下载失败 {file_path}: {str(last_error)}")
        return False
