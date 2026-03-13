import os

def find_video(folder_path: str):
  return [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
