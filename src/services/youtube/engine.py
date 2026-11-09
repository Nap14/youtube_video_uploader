import os
from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple
from send2trash import send2trash

from src.core.context import AppContext
from src.services.base_processor import BaseProcessor
from src.services.file_utils import find_video
from src.services.schedule_utils import get_course_name_by_date, get_date_from_file_name
from .data.result import UploadResult
from .data.status import UploadStatus
from .playlist import PlaylistController
from .video import VideoService

class YoutubeProcessor(BaseProcessor):
    def __init__(self, vs: VideoService, pc: PlaylistController, ctx: AppContext, error_cb: Optional[Callable[[str, str], None]] = None):
        super().__init__(ctx, error_cb)
        self.vs = vs
        self.pc = pc

    def process(self, progress_cb: Optional[Callable[[str, Tuple[int, int]], None]] = None) -> List[List[Any]]:
        zoom_dir = self.ctx.config.get_zoom_dir()
        if not zoom_dir or not os.path.exists(zoom_dir):
            self._handle_missing_dir(zoom_dir)
            return []
            
        folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
        folders.sort()
        
        if progress_cb:
            self.ctx.logger.info(f"Found {len(folders)} video folders to process.")
            progress_cb(f"Processing...", (0, len(folders)))

        # Pre-scan to group multiple recordings in the same lesson slot
        slot_map = {}
        for folder in folders:
            folder_path = os.path.join(zoom_dir, folder)
            mp4 = find_video(folder_path)
            if not mp4:
                continue
            v_date = get_date_from_file_name(folder)
            if not v_date:
                continue
            meta = get_course_name_by_date(v_date, self.ctx.schedule)
            if not meta:
                continue
            c_name = meta if isinstance(meta, str) else meta.get("name", "Unknown")
            slot_time = meta.get("start_time", "") if isinstance(meta, dict) else ""
            slot_key = (v_date.strftime('%Y-%m-%d'), c_name, slot_time)
            if slot_key not in slot_map:
                slot_map[slot_key] = []
            slot_map[slot_key].append(folder)

        folder_part_suffix = {}
        for slot_key, slot_folder_list in slot_map.items():
            if len(slot_folder_list) > 1:
                for idx, f_name in enumerate(slot_folder_list):
                    folder_part_suffix[f_name] = f" Ч{idx + 1}"
            else:
                folder_part_suffix[slot_folder_list[0]] = ""

        results: List[UploadResult] = []
        
        for i, folder in enumerate(folders):
            if progress_cb:
                progress_cb(f"Processsing: {folder}", (i + 1, len(folders)))
                
            part_suffix = folder_part_suffix.get(folder, "")
            res = self._process_folder(folder, os.path.join(zoom_dir, folder), progress_cb, part_suffix=part_suffix)
            if res:
                results.append(res)
                
        return [r.to_list() for r in results]

    def _handle_missing_dir(self, zoom_dir: Optional[str]):
        msg = f"Zoom videos directory not found: '{zoom_dir}'\nCheck 'ZOOM_DIR' in settings."
        self._report_error("Directory Error", msg)

    def _process_folder(self, name: str, path: str, progress_cb: Optional[Callable] = None, part_suffix: str = "") -> Optional[UploadResult]:
        mp4 = find_video(path)
        if not mp4:
            return None
            
        v_date = get_date_from_file_name(name)
        d_str = v_date.strftime('%d.%m.%Y %H:%M') if v_date else "N/A"
        time_str = v_date.strftime('%H:%M') if v_date else "Unknown"
        
        self.ctx.logger.info(f"Checking folder: {name} | Time: {time_str}")
        if progress_cb:
            progress_cb(f"Folder: {name}", (0, 1))

        meta = None
        if v_date:
            meta = get_course_name_by_date(v_date, self.ctx.schedule)
            
        if not meta:
            if progress_cb:
                self.ctx.logger.info(f"No course match in calendar for {d_str}")
            return UploadResult(d_str, "Skipped", "", UploadStatus.SKIPPED, "Not in schedule")
            
        c_name = meta if isinstance(meta, str) else meta.get("name", "Unknown")
        
        self.ctx.logger.info(f"Matched Course: {c_name}{part_suffix}")
            
        return self._check_marker_or_upload(path, mp4[0], v_date, meta, d_str, c_name, progress_cb, part_suffix=part_suffix)

    def _check_marker_or_upload(self, path, mp4_file, v_date, meta, d_str, c_name, progress_cb: Optional[Callable] = None, part_suffix: str = ""):
        display_name = f"{c_name}{part_suffix}" if part_suffix else c_name
        marker = os.path.join(path, ".uploaded_to_youtube")
        if os.path.exists(marker):
            with open(marker, 'r', encoding='utf-8') as f:
                vid = f.read().strip()
            self.ctx.logger.info(f"Already uploaded earlier: {display_name} (ID: {vid})")
            return UploadResult(d_str, display_name, f"https://youtu.be/{vid}", UploadStatus.ALREADY_UPLOADED)
            
        try:
            return self._upload(path, mp4_file, v_date, meta, d_str, c_name, progress_cb, part_suffix=part_suffix)
        except Exception as e:
            self.ctx.logger.error(f"Upload error {os.path.basename(path)}: {e}")
            return UploadResult(d_str, display_name, "", UploadStatus.FAIL, str(e))

    def _upload(self, path: str, mp4_rel: str, v_date: datetime, meta: Any, d_str: str, c_name: str, progress_cb: Optional[Callable] = None, part_suffix: str = "") -> UploadResult:
        full_path = os.path.join(path, mp4_rel)
        title = f"{c_name}/{v_date.strftime('%d.%m.%Y')}{part_suffix}"
        
        self.ctx.logger.info(f"Uploading {title} to YouTube...")
        vid, url = self.vs.upload(full_path, title, f"Lesson: {c_name}")
        self._apply_thumbnail(vid, meta)
        
        with open(os.path.join(path, ".uploaded_to_youtube"), 'w', encoding='utf-8') as f:
            f.write(vid)
            
        self.pc.add_video(vid, c_name)
        send2trash(os.path.normpath(path))
        
        self.ctx.logger.info(f"Upload Complete: {url}")
            
        display_name = f"{c_name}{part_suffix}" if part_suffix else c_name
        return UploadResult(d_str, display_name, url, UploadStatus.SUCCESS)

    def _apply_thumbnail(self, vid: str, meta: Any):
        if isinstance(meta, str):
            return
            
        thumb = meta.get("thumbnail")
        if not thumb:
            return
            
        t_path = thumb
        if not os.path.isabs(thumb):
            t_path = os.path.join(self.ctx.paths.base_dir, "thumbnails", thumb)
            
        if os.path.exists(t_path):
            self.vs.set_thumbnail(vid, t_path)
