import os

from googleapiclient.http import MediaFileUpload


class VideoService:
  def __init__(self, youtube, logging):
      self.youtube = youtube
      self.logging = logging

  def upload_video(self, file_path, title, description, category_id="27"):
      """
      Завантажує відео на YouTube.
      Значення category_id="27" відповідає Education.
      """
      self.logging.info(f"Спроба завантаження: {title}")
      
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
              self.logging.info(f"Завантажено: {int(status.progress() * 100)}%")

      self.logging.info("Завантаження завершено!")
      video_id = response.get('id')
      return video_id, f"https://youtu.be/{video_id}"
  
  def set_video_thumbnail(self, video_id, thumbnail_path):
      """
      Встановлює кастомну обкладику для відео.
      """
      if not thumbnail_path or not os.path.exists(thumbnail_path):
          self.logging.warning(f"Обкладинку не знайдено за шляхом: {thumbnail_path}. Залишаємо стандартну.")
          return
          
      self.logging.info(f"Встановлюємо обкладинку: {thumbnail_path}")
      try:
          request = self.youtube.thumbnails().set(
              videoId=video_id,
              media_body=MediaFileUpload(thumbnail_path)
          )
          request.execute()
          self.logging.info("Обкладинку успішно встановлено!")
      except Exception as e:
          self.logging.error(f"Помилка встановлення обкладинки: {e}")