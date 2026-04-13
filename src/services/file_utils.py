import os, sys

def find_video(folder_path):
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.mp4', '.mkv')):
            return [f]
    return []

def get_base_dir(file_path):
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(file_path))