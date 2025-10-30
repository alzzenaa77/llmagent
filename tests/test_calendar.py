from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate():
    """Authenticate dan return credentials"""
    creds = None
    
    # Cek apakah token.json sudah ada
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Kalau belum ada atau tidak valid, minta user login
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Simpan token untuk next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def test_add_event():
    """Test tambah event ke Google Calendar"""
    print("🔐 Authenticating...")
    creds = authenticate()
    
    print("📅 Creating Calendar service...")
    service = build('calendar', 'v3', credentials=creds)
    
    # Buat event besok jam 2 siang
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    event = {
        'summary': '🤖 Test Event dari Bot',
        'description': 'Event ini dibuat otomatis oleh StudyScheduler Bot',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Jakarta',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Jakarta',
        },
    }
    
    print("✨ Adding event to calendar...")
    result = service.events().insert(calendarId='primary', body=event).execute()
    
    print(f"\n✅ SUCCESS! Event created:")
    print(f"   📌 Title: {event['summary']}")
    print(f"   🕐 Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   🔗 Link: {result.get('htmlLink')}")

if __name__ == '__main__':
    test_add_event()