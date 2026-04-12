import os

def find_video(folder_path):
    # Find first mp4 or mkv file in folder
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.mp4', '.mkv')):
            return [f]
    return []
