from googleapiclient.http import MediaFileUpload

class VideoService:
    def __init__(self, youtube, logger):
        self.youtube = youtube
        self.logger = logger

    def upload(self, path, title, description):
        body = {
            'snippet': {'title': title, 'description': description, 'categoryId': '27'},
            'status': {'privacyStatus': 'unlisted', 'selfDeclaredMadeForKids': False}
        }
        media = MediaFileUpload(path, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(part='snippet,status', body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: self.logger.info(f"Uploading... {int(status.progress() * 100)}%")
            
        video_id = response.get('id')
        return video_id, f"https://youtu.be/{video_id}"

    def set_thumbnail(self, video_id, img_path):
        try:
            self.youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(img_path)).execute()
            self.logger.info("Thumbnail updated.")
        except Exception as e:
            self.logger.error(f"Thumbnail error: {e}")
