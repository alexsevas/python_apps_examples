# Глобальный планировщик событий с учётом часовых поясов


from datetime import datetime
import pytz
from tabulate import tabulate

# 🔹 Ввод времени события (локальное время организатора)
event_time_str = "2025-04-10 14:00"  # формат: YYYY-MM-DD HH:MM
organizer_timezone = "Europe/Moscow"

# 🔹 Часовые пояса участников
timezones = [
    "Europe/Moscow",
    "Asia/Tokyo",
    "America/New_York",
    "Europe/London",
    "Australia/Sydney",
    "Asia/Dubai"
]

# 🔹 Парсим локальное время организатора
local_tz = pytz.timezone(organizer_timezone)
local_dt = local_tz.localize(datetime.strptime(event_time_str, "%Y-%m-%d %H:%M"))

# 🔹 Конвертация
table = []
for tz_name in timezones:
    tz = pytz.timezone(tz_name)
    converted = local_dt.astimezone(tz)
    table.append([tz_name, converted.strftime("%Y-%m-%d %H:%M")])

# 🔹 Вывод
print(f"\n🕒 Время события (локально): {local_dt.strftime('%Y-%m-%d %H:%M')} [{organizer_timezone}]\n")
print(tabulate(table, headers=["Часовой пояс", "Местное время"]))
