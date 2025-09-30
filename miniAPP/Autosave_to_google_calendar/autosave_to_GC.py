'''
Автозапись задач в Google Calendar из списка дел.
Берёт список задач с указанием времени и автоматически добавляет их в ваш Google Calendar. Идеально для ассистентов,
скриптов автопланирования и напоминалок.

pip install google-api-python-client google-auth

Нужен [service account JSON](https://console.cloud.google.com/), доступ к календарю и расшаривание CALENDAR_ID.
'''

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
CALENDAR_ID = 'primary'

todo_list = [
    {"task": "Сдать отчёт", "start_in_minutes": 15, "duration": 30},
    {"task": "Позвонить клиенту", "start_in_minutes": 60, "duration": 15},
]

def add_event(service, summary, start_time, duration_minutes):
    end_time = start_time + timedelta(minutes=duration_minutes)
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Moscow'}
    }
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.now()
    for item in todo_list:
        start_time = now + timedelta(minutes=item['start_in_minutes'])
        add_event(service, item['task'], start_time, item['duration'])

if __name__ == '__main__':
    main()
