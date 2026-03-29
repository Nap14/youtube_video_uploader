class PlaylistController:
    def __init__(self, youtube, logging):
        self.youtube = youtube
        self.logging = logging

    def create_playlist(self, playlist_title: str):
        body = {
            "snippet": {
                "title": playlist_title,
                "description": f"Automatic lesson recordings for {playlist_title}"
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
                    self.logging.info(f"Playlist found: {playlist_title}")
                    return item["id"]
            request = self.youtube.playlists().list_next(request, response)

    def get_or_create_playlist(self, playlist_title):
        """Finds a playlist by title; if not found, creates one (Unlisted)."""
        self.logging.info(f"Searching for playlist: '{playlist_title}'")
        playlist = self.find_playlist(playlist_title)
        if playlist:
            return playlist
            
        self.logging.info(f"Playlist not found. Creating: '{playlist_title}'")
        return self.create_playlist(playlist_title)
    
    def add_video_to_playlist(self, video_id, playlist_title):
        """Adds a video to the playlist."""
        self.logging.info(f"Adding video {video_id} to playlist {playlist_title}")
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
        self.logging.info("Video successfully added to the playlist.")