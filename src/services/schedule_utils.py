import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

def load_schedule(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_schedule(path: str, data: Dict[str, Any]):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_date_from_file_name(name: str) -> Optional[datetime]:
    try:
        dt_str = " ".join(name.split()[:2])
        return datetime.strptime(dt_str, '%Y-%m-%d %H.%M.%S')
    except:
        return None

def get_course_name_by_date(date: datetime, schedule: Dict[str, Any]) -> Optional[Any]:
    day_lessons = schedule.get(date.strftime('%A'), {})
    v_min = date.hour * 60 + date.minute
    
    for t_str, l_data in day_lessons.items():
        try:
            h, m = map(int, t_str.split(':'))
            l_min = h * 60 + m
            if (l_min - 5) <= v_min <= (l_min + 30):
                return l_data
        except:
            continue
    return None
