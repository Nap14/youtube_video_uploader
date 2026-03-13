import json
import os
import datetime



def load_schedule(file: str, logging):
    """Завантажує розклад з файлу JSON."""
    if not os.path.exists(file):
         print("\n" + "!"*50)
         print(f"ПОМИЛКА: Файл розкладу '{file}' не знайдено!")
         print("Будь ласка, створіть цей файл у форматі JSON.")
         print("Приклад структури можна знайти в README.md.")
         print("!"*50 + "\n")
         logging.error(f"Файл розкладу {file} не знайдено. Перезапустіть програму після створення файлу.")
         input("Натисніть Enter, щоб вийти...")
         exit(1)
    with open(file, 'r', encoding='utf-8') as f:
         return json.load(f)
    

def get_course_name_by_date(folder_date, schedule):
    """
    Визначає курс на основі дати та часу створення запису.
    Повертає словник з даними курсу (назва, шлях до обкладинки) або None.
    """
    day_name = folder_date.strftime('%A') 
    time_str = folder_date.strftime('%H:%M')
    
    day_schedule = schedule.get(day_name, {})
    
    course = day_schedule.get(time_str)
    if course:
         return course
    
    for scheduled_time_str, course_name in day_schedule.items():
         scheduled_time = datetime.datetime.strptime(scheduled_time_str, '%H:%M').time()
         scheduled_datetime = datetime.datetime.combine(folder_date.date(), scheduled_time)
         
         time_difference = abs((folder_date - scheduled_datetime).total_seconds())
         if time_difference <= 10 * 60:
             return course_name
    
    return None

def get_date_from_file_name(file_name: str):
  date_str = file_name[:19]
  try:
      return datetime.datetime.strptime(date_str, '%Y-%m-%d %H.%M.%S')
  except ValueError:
      return