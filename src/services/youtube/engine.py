from src.services.file_utils import get_base_dir
import os
from send2trash import send2trash
from typing import List, Callable, Optional, Tuple, Any

from src.core.config import Config
from src.services.file_utils import find_video
from src.services.youtube.video import VideoService
from src.services.youtube.playlist import PlaylistController
from src.services.schedule_utils import get_course_name_by_date, get_date_from_file_name

from .data.status import UploadStatus
from .data.result import UploadResult

class YoutubeProcessor:
    def __init__(
        self, 
        video_service: VideoService, 
        playlist_controller: PlaylistController, 
        config: Config, 
        schedule: dict, 
        logger,
        root_dir: str,
        error_cb: Optional[Callable[[str, str], None]] = None
    ):
        self.vs = video_service
        self.pc = playlist_controller
        self.config = config
        self.schedule = schedule
        self.logger = logger
        self.root_dir = root_dir
        self.error_cb = error_cb

    def process(self, progress_cb: Optional[Callable[[str, Tuple[int, int]], None]] = None) -> List[List[Any]]:
        zoom_dir = self.config.get_zoom_dir()
        if not zoom_dir or not os.path.exists(zoom_dir):
            msg = f"Zoom videos directory not found: '{zoom_dir}'\nPlease check 'ZOOM_DIR' in your settings."
            self.logger.error(msg)
            if self.error_cb:
                self.error_cb("Directory Error", msg)
            return []

        folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
        self.logger.info(f"Found {len(folders)} folders to process in {zoom_dir}")
        results: List[UploadResult] = []
        total = len(folders)

        for i, folder in enumerate(folders):
            folder_path = os.path.join(zoom_dir, folder)
            
            if progress_cb:
                progress_cb(f"Processing YouTube: {folder}", (i + 1, total))

            result = self._process_folder(folder, folder_path)
            if result:
                results.append(result)

        return [r.to_list() for r in results]

    def _process_folder(self, folder_name: str, folder_path: str) -> Optional[UploadResult]:
        mp4_files = find_video(folder_path)
        if not mp4_files:
            return None

        video_date = get_date_from_file_name(folder_name)
        date_str = video_date.strftime('%d.%m.%Y %H:%M') if video_date else "N/A"
        
        course_data = get_course_name_by_date(video_date, self.schedule) if video_date else None
        if not course_data:
            self.logger.info(f"No schedule match for '{folder_name}'. Marked as PRIVATE skipped.")
            return UploadResult(date_str, "Private/Unknown", "", UploadStatus.SKIPPED, "Private (not in schedule)")

        name = course_data if isinstance(course_data, str) else course_data.get("name", "Unknown")
        
        marker_path = os.path.join(folder_path, ".uploaded_to_youtube")
        if os.path.exists(marker_path):
            with open(marker_path, 'r') as f:
                vid = f.read().strip()
            return UploadResult(date_str, name, f"https://youtu.be/{vid}", UploadStatus.ALREADY_UPLOADED)

        try:
            return self._execute_upload(folder_path, folder_name, mp4_files[0], video_date, course_data, date_str, name)
        except Exception as e:
            self.logger.error(f"Upload error {folder_name}: {e}")
            return UploadResult(date_str, name, "", UploadStatus.FAIL, str(e))

    def _execute_upload(self, folder_path: str, folder_name: str, mp4_rel_path: str, video_date: Any, course_data: Any, date_str: str, name: str) -> UploadResult:
        self.logger.info(f"Uploading '{name}' ({video_date.strftime('%d.%m.%Y')})...")
        
        full_video_path = os.path.join(folder_path, mp4_rel_path)
        title = f"{name}/{video_date.strftime('%d.%m.%Y')}"
        description = f"Lesson: {name}"
        
        vid, url = self.vs.upload(full_video_path, title, description)
        
        thumb = None if isinstance(course_data, str) else course_data.get("thumbnail")
        if thumb:
            if not os.path.isabs(thumb):
                thumb = os.path.join(self.root_dir, "thumbnails", thumb)
            
            if os.path.exists(thumb):
                self.logger.info(f"Setting thumbnail: {os.path.basename(thumb)}")
                self.vs.set_thumbnail(vid, thumb)
            else:
                self.logger.warning(f"Thumbnail not found: {thumb}")

        marker_path = os.path.join(folder_path, ".uploaded_to_youtube")
        with open(marker_path, 'w') as f:
            f.write(vid)
            
        self.pc.add_video(vid, name)
        self.logger.info(f"SUCCESS: '{name}' uploaded to YouTube.")
        
        send2trash(os.path.normpath(folder_path))
        return UploadResult(date_str, name, url, UploadStatus.SUCCESS)
