import json
import os
from datetime import datetime

def load_schedule(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_date_from_file_name(name):
    try:
        dt_str = " ".join(name.split()[:2])
        return datetime.strptime(dt_str, '%Y-%m-%d %H.%M.%S')
    except: return None

def get_course_name_by_date(date, schedule):
    day = date.strftime('%A')
    day_lessons = schedule.get(day, {})
    
    # Matching simple HH:MM
    time_key = date.strftime('%H:00')
    if time_key in day_lessons: return day_lessons[time_key]
    
    time_key_30 = date.strftime('%H:30')
    if time_key_30 in day_lessons: return day_lessons[time_key_30]
    
    return None
