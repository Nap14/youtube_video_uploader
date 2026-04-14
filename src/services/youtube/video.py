from typing import Any, Tuple
from googleapiclient.http import MediaFileUpload

from src.core.logger import Logger

class VideoService:
    def __init__(self, youtube: Any, logger: Logger):
        self.youtube = youtube
        self.logger = logger

    def upload(self, path: str, title: str, description: str) -> Tuple[str, str]:
        body = {
            'snippet': {'title': title, 'description': description, 'categoryId': '27'},
            'status': {'privacyStatus': 'unlisted', 'selfDeclaredMadeForKids': False}
        }
        media = MediaFileUpload(path, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(part='snippet,status', body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                self.logger.info(f"Uploading... {int(status.progress() * 100)}%")
        vid = response.get('id')
        return vid, f"https://youtu.be/{vid}"

    def set_thumbnail(self, video_id: str, img_path: str) -> None:
        try:
            self.youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(img_path)).execute()
            self.logger.info("Thumbnail updated.")
        except Exception as e:
            self.logger.error(f"Thumbnail error: {e}")
