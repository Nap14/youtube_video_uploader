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
        exe_dir = os.path.dirname(sys.executable)
        if "Contents/MacOS" in exe_dir:
            return os.path.abspath(os.path.join(exe_dir, "../../.."))
        if not os.path.exists(os.path.join(exe_dir, "configs")):
            parent_dir = os.path.abspath(os.path.join(exe_dir, ".."))
            if os.path.exists(os.path.join(parent_dir, "configs")):
                return parent_dir
        return exe_dir
    return os.path.dirname(os.path.abspath(file_path))