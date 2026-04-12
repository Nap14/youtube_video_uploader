import os

def find_video(folder_path):
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.mp4', '.mkv')):
            return [f]
    return []
