class PlaylistController:
    def __init__(self, youtube, logging):
        self.youtube = youtube
        self.logging = logging

    def create_playlist(self, playlist_title: str):
        body = {
            "snippet": {
                "title": playlist_title,
                "description": f"Автоматичні записи занять для {playlist_title}"
            },
            "status": {
                "privacyStatus": "unlisted"
            }
        }
        response = self.youtube.playlists().insert(
            part="snippet,status",
            body=body
        ).execute()
        
        return response["id"] 
    
    def find_playlist(self, playlist_title: str):
        request = self.youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        
        while request is not None:
            response = request.execute()
            for item in response.get("items", []):
                if item["snippet"]["title"] == playlist_title:
                    self.logging.info(f"Знайдено плейлист: {playlist_title}")
                    return item["id"]
            request = self.youtube.playlists().list_next(request, response)

    def get_or_create_playlist(self, playlist_title):
        """Шукає плейлист за назвою, якщо немає - створює (Unlisted)."""
        self.logging.info(f"Шукаємо плейлист: '{playlist_title}'")
        playlist = self.find_playlist(playlist_title)
        if playlist:
            return playlist
            
        self.logging.info(f"Плейлист не знайдено. Створюємо: '{playlist_title}'")
        return self.create_playlist(playlist_title)
    
    def add_video_to_playlist(self, video_id, playlist_title):
        """Додає відео в плейлист."""
        self.logging.info(f"Додаємо відео {video_id} у плейлист {playlist_title}")
        playlist_id = self.get_or_create_playlist(playlist_title)
        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        self.youtube.playlistItems().insert(
            part="snippet",
            body=body
        ).execute()
        self.logging.info("Відео успішно додано у плейлист.")