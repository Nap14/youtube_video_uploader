import os

from googleapiclient.http import MediaFileUpload


class VideoService:
  def __init__(self, youtube, logging):
      self.youtube = youtube
      self.logging = logging

  def upload_video(self, file_path, title, description, category_id="27"):
      """
      Uploads a video to YouTube.
      category_id="27" corresponds to Education.
      """
      self.logging.info(f"Attempting upload: {title}")
      
      body = {
          'snippet': {
              'title': title,
              'description': description,
              'categoryId': category_id
          },
          'status': {
              'privacyStatus': 'unlisted',
              'selfDeclaredMadeForKids': False
          }
      }

      media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')

      request = self.youtube.videos().insert(
          part=','.join(body.keys()),
          body=body,
          media_body=media
      )

      response = None
      while response is None:
          status, response = request.next_chunk()
          if status:
              self.logging.info(f"Uploaded: {int(status.progress() * 100)}%")

      self.logging.info("Upload complete!")
      video_id = response.get('id')
      return video_id, f"https://youtu.be/{video_id}"
  
  def set_video_thumbnail(self, video_id, thumbnail_path):
      """
      Sets a custom thumbnail for the video.
      """
      if not thumbnail_path or not os.path.exists(thumbnail_path):
          self.logging.warning(f"Thumbnail not found at: {thumbnail_path}. Keeping default.")
          return
          
      self.logging.info(f"Setting thumbnail: {thumbnail_path}")
      try:
          request = self.youtube.thumbnails().set(
              videoId=video_id,
              media_body=MediaFileUpload(thumbnail_path)
          )
          request.execute()
          self.logging.info("Thumbnail successfully set!")
      except Exception as e:
          self.logging.error(f"Помилка встановлення обкладинки: {e}")