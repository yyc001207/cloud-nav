import re
from pathlib import Path
from urllib.parse import quote
from typing import Dict, Any
import asyncio
import shutil
import os
from app.business.openlist.openlist_api import OpenListAPI
from app.business.openlist.task_status_manager import TaskStatusManager
from app.core.logger import get_strm_logger
from app.utils.helpers import sanitize_filename


class STRMGenerator:
    def _sanitize_path(self, path: str) -> str:
        if not path or path == ".":
            return path
        parts = path.split("/")
        cleaned_parts = [sanitize_filename(p) for p in parts]
        return "/".join(cleaned_parts)

    def __init__(self, global_config: Dict[str, Any], task_config: Dict[str, Any], task_id: str = None):
        self.logger = get_strm_logger()
        self.task_id = task_id
        self.base_url = global_config["baseUrl"].rstrip("/")
        self.api = OpenListAPI(self.base_url, global_config["token"])
        self.video_exts = global_config.get("videoExtensions", [])
        self.subtitle_exts = global_config.get("subtitleExtensions", [])
        self.output_dir = task_config.get("outputDir") or "./output"
        task_paths_str = task_config.get("taskPaths", "")
        self.task_paths = [p.strip() for p in task_paths_str.split("\n") if p.strip()]
        self.stats = {"totalVideos": 0, "successVideos": 0, "errorVideos": 0, "totalSubtitles": 0, "successSubtitles": 0, "errorSubtitles": 0}

    def _get_download_url(self, file_path: str) -> str:
        clean_path = file_path.strip("/")
        return f"{self.base_url}/d/{quote(clean_path)}"

    def _build_output_dir(self, output_base: Path, relative_path: str) -> Path:
        relative_path = str(relative_path).replace("\\", "/").strip("./")
        if not relative_path or relative_path == ".":
            output_dir = output_base
        else:
            parts = relative_path.split("/")
            cleaned_parts = [sanitize_filename(p) for p in parts]
            cleaned_path = "/".join(cleaned_parts)
            output_dir = output_base / cleaned_path
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _cancelled(self) -> bool:
        if self.task_id:
            return TaskStatusManager.is_cancelled(self.task_id)
        return False

    def _get_output_path(self, item_path: str, base_path: str) -> str:
        item_path = item_path.strip("/")
        base_path = base_path.strip("/")
        if item_path.startswith(base_path):
            relative = item_path[len(base_path):].lstrip("/")
            if not relative:
                return Path(item_path).name
            return relative
        return Path(item_path).name

    async def _process_file(self, item: Dict, current_path: str, output_base: Path, force: bool, base_path: str):
        name = item.get("name", "")
        file_ext = Path(name).suffix.lower()
        item_path = item.get("path") or f"{current_path}/{name}"
        item_path = item_path.strip("/")
        if self._cancelled():
            return
        output_relative = self._get_output_path(item_path, base_path)
        parent = Path(output_relative).parent
        output_dir_path = str(parent).replace("\\", "/") if str(parent) != "." else ""
        output_dir = self._build_output_dir(output_base, output_dir_path)

        if file_ext in self.video_exts:
            self.stats["totalVideos"] += 1
            try:
                strm_filename = self._sanitize_path(Path(name).stem) + ".strm"
                strm_path = output_dir / strm_filename
                if not force and strm_path.exists():
                    self.stats["successVideos"] += 1
                    self.logger.info(f"[{output_relative}] 跳过 STRM (已存在): {name}")
                    return
                output_dir.mkdir(parents=True, exist_ok=True)
                with open(strm_path, "w", encoding="utf-8") as f:
                    f.write(self._get_download_url(item_path))
                self.stats["successVideos"] += 1
                self.logger.info(f"[{output_relative}] 创建 STRM: {name}")
            except Exception as e:
                self.stats["errorVideos"] += 1
                self.logger.error(f"[{output_relative}] 创建 STRM 失败 {name}: {e}")
        elif file_ext in self.subtitle_exts:
            self.stats["totalSubtitles"] += 1
            try:
                subtitle_path = output_dir / name
                if not force and subtitle_path.exists():
                    self.stats["successSubtitles"] += 1
                    self.logger.info(f"[{output_relative}] 跳过字幕 (已存在): {name}")
                    return
                output_dir.mkdir(parents=True, exist_ok=True)
                success = await self.api.download_file("/" + item_path, str(subtitle_path), encode=False)
                if success:
                    self.stats["successSubtitles"] += 1
                    self.logger.info(f"[{output_relative}] 下载字幕: {name}")
                else:
                    self.stats["errorSubtitles"] += 1
                    self.logger.error(f"[{output_relative}] 下载字幕失败: {name}")
            except Exception as e:
                self.stats["errorSubtitles"] += 1
                self.logger.error(f"[{output_relative}] 下载字幕失败 {name}: {e}")

    IGNORE_EXTS = {".nfo", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".svg", ".ico", ".mp3"}

    async def _scan_and_process(self, scan_path: str, output_base: Path, force: bool, base_path: str, cloud_files: set):
        if self._cancelled():
            return
        try:
            result = await self.api.list_files("/" + scan_path)
            items = result.get("content") or []
        except Exception as e:
            self.logger.error(f"扫描失败 {scan_path}: {e}，清理本地残留")
            self._cleanup_current_dir(output_base, set(), base_path, scan_path, set())
            return
        cloud_dir_names = set()
        for item in items:
            if not item.get("is_dir", False):
                item_name = item.get("name", "")
                item_path = f"{scan_path}/{item_name}"
                relative_path = self._get_output_path(item_path, base_path)
                relative_path = self._sanitize_path(relative_path)
                file_ext = Path(relative_path).suffix.lower()
                if file_ext in self.video_exts:
                    relative_path = str(relative_path).rsplit(".", 1)[0] + ".strm"
                cloud_files.add(relative_path)
            else:
                dir_name = item.get("name", "")
                cloud_dir_names.add(self._sanitize_path(dir_name))
        for item in items:
            if item.get("is_dir", False):
                subdir_name = item.get("name", "")
                subdir_path = item.get("path", "").strip("/") or f"{scan_path}/{subdir_name}"
                sub_cloud_files = set()
                await self._scan_and_process(subdir_path, output_base, force, base_path, sub_cloud_files)
                if sub_cloud_files:
                    cloud_files.update(sub_cloud_files)
        self._cleanup_current_dir(output_base, cloud_files, base_path, scan_path, cloud_dir_names)
        tasks = [self._process_file(item, scan_path, output_base, force, base_path) for item in items if not item.get("is_dir", False)]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _cleanup_current_dir(self, output_base: Path, cloud_files: set, base_path: str, scan_path: str, cloud_dir_names: set = None):
        output_relative = self._get_output_path(scan_path, base_path)
        output_relative = self._sanitize_path(output_relative)
        current_dir = output_base / output_relative
        if not current_dir.exists():
            return
        current_depth = len(output_relative.split("/")) if output_relative else 0
        current_dir_files = set()
        for cf in cloud_files:
            cf_parts = cf.split("/")
            if len(cf_parts) > current_depth:
                prefix = "/".join(cf_parts[:current_depth])
                if current_depth == 0 or prefix == output_relative:
                    current_dir_files.add(cf)
        for local_file in current_dir.iterdir():
            if not local_file.is_file():
                continue
            try:
                relative_path = local_file.relative_to(output_base)
            except ValueError:
                continue
            relative_str = str(relative_path).replace("\\", "/")
            file_ext = Path(relative_str).suffix.lower()
            if file_ext in self.IGNORE_EXTS:
                continue
            if file_ext == ".strm":
                if relative_str in current_dir_files:
                    continue
                try:
                    local_file.unlink()
                    self.logger.info(f"删除已失效STRM: {relative_str}")
                except Exception as e:
                    self.logger.error(f"删除文件失败 {local_file}: {e}")
                continue
            if relative_str not in current_dir_files:
                try:
                    local_file.unlink()
                    self.logger.info(f"删除已失效文件: {relative_str}")
                except Exception as e:
                    self.logger.error(f"删除文件失败 {local_file}: {e}")
        if cloud_dir_names is not None:
            for local_item in current_dir.iterdir():
                if local_item.is_dir():
                    sanitized_name = self._sanitize_path(local_item.name)
                    if sanitized_name not in cloud_dir_names:
                        try:
                            shutil.rmtree(str(local_item))
                            self.logger.info(f"删除已失效目录: {local_item}")
                        except Exception as e:
                            self.logger.error(f"删除目录失败 {local_item}: {e}")

    def _cleanup_empty_dirs(self, output_base: Path):
        for dirpath, dirnames, filenames in os.walk(str(output_base), topdown=False):
            current = Path(dirpath)
            if current == output_base:
                continue
            try:
                if not any(current.iterdir()):
                    current.rmdir()
                    self.logger.info(f"清理空目录: {current}")
            except Exception as e:
                self.logger.error(f"清理空目录失败 {current}: {e}")

    async def execute(self, force: bool = False, cleanup: bool = True) -> Dict[str, Any]:
        if self.output_dir.startswith("/"):
            relative_path = self.output_dir.lstrip("/")
            output_path = Path.cwd() / "output" / relative_path
            output_path.mkdir(parents=True, exist_ok=True)
            self.output_dir = str(output_path)
        output_base = Path(self.output_dir)
        self.logger.info(f"开始执行，共 {len(self.task_paths)} 个路径")
        for task_path in self.task_paths:
            if self._cancelled():
                self.logger.info("任务已取消")
                break
            base_path = task_path.strip("/")
            cloud_files = set()
            await self._scan_and_process(task_path, output_base, force, base_path, cloud_files)
        self._cleanup_empty_dirs(output_base)
        self.logger.info(f"完成: 视频 {self.stats['successVideos']}/{self.stats['totalVideos']}, 字幕 {self.stats['successSubtitles']}/{self.stats['totalSubtitles']}")
        return self.stats
