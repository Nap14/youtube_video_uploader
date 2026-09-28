import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

_SCHEDULE_TEMPLATE = {
    "_comment": "Приклад розкладу. Замініть на ваші дані та видаліть це поле.",
    "Monday": {
        "16:10": {
            "name": "Назва курсу",
            "thumbnail": "thumbnail.png",
            "lms_course_id": "123456"
        }
    }
}

def load_schedule(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        _create_default_schedule(path)
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _create_default_schedule(path: str):
    """Create schedule.json with an example template."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(_SCHEDULE_TEMPLATE, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

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
    
    parsed_lessons = []
    for t_str, l_data in day_lessons.items():
        try:
            h, m = map(int, t_str.split(':'))
            parsed_lessons.append((h * 60 + m, t_str, l_data))
        except:
            continue
    parsed_lessons.sort(key=lambda x: x[0])
    
    for i, (l_min, t_str, l_data) in enumerate(parsed_lessons):
        start_min = l_min - 5
        duration = 50
        if isinstance(l_data, dict):
            duration = int(l_data.get("duration", 50))
            
        if i + 1 < len(parsed_lessons):
            next_l_min = parsed_lessons[i + 1][0]
            end_min = min(l_min + duration + 5, next_l_min - 5)
        else:
            end_min = l_min + duration + 5
            
        if start_min <= v_min < end_min:
            if isinstance(l_data, dict):
                res = dict(l_data)
                res["start_time"] = t_str
                return res
            return l_data
            
    return None
