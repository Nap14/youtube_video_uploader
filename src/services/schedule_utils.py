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
    
    video_time = date.hour * 60 + date.minute
    
    for time_str, lesson_data in day_lessons.items():
        try:
            h, m = map(int, time_str.split(':'))
            lesson_time = h * 60 + m
            
            # Range: [lesson_time - 5, lesson_time + 30]
            if (lesson_time - 5) <= video_time <= (lesson_time + 30):
                return lesson_data
        except: continue
        
    return None
