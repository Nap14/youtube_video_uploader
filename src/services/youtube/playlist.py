class PlaylistController:
    def __init__(self, youtube, logger):
        self.youtube, self.logger = youtube, logger

    def create(self, title):
        body = {
            "snippet": {"title": title, "description": f"Recordings for {title}"},
            "status": {"privacyStatus": "unlisted"}
        }
        res = self.youtube.playlists().insert(part="snippet,status", body=body).execute()
        return res["id"] 
    
    def find(self, title):
        req = self.youtube.playlists().list(part="snippet", mine=True, maxResults=50)
        while req:
            res = req.execute()
            for item in res.get("items", []):
                if item["snippet"]["title"] == title: return item["id"]
            req = self.youtube.playlists().list_next(req, res)
        return None

    def add_video(self, video_id, title):
        pid = self.find(title) or self.create(title)
        body = {
            "snippet": {
                "playlistId": pid,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
        self.youtube.playlistItems().insert(part="snippet", body=body).execute()
        self.logger.info(f"Video {video_id} added to playlist '{title}'")
