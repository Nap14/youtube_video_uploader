import os
import sys
from typing import List

def find_video(folder_path: str) -> List[str]:
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.mp4', '.mkv')):
            return [f]
    return []

def get_base_dir(file_path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(file_path))