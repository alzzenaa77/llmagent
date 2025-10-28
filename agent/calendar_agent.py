from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarAgent:
    """Google Calendar Agent for CRUD operations"""
    
    def __init__(self, credentials_path='credentials/credentials.json', 
                 token_path='credentials/token.json',
                 timezone='Asia/Jakarta'):
        """
        Initialize Calendar Agent
        
        Args:
            credentials_path: Path to credentials.json
            token_path: Path to token.json
            timezone: Timezone for events
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.timezone = timezone
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Check if token.json exists
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Download from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("✅ Google Calendar authenticated")
    
    def create_event(self, title, date, time, duration=60, description=""):
        """
        CREATE - Create new event
        
        Args:
            title: Event title
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            duration: Duration in minutes
            description: Event description
        """
        try:
            start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': self.timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': result.get('id'),
                'link': result.get('htmlLink'),
                'message': f"✅ **Event created!**\n\n📝 **Title:** {title}\n📅 **Date:** {date}\n🕐 **Time:** {time}\n⏱️ **Duration:** {duration} minutes\n🆔 **ID:** `{result.get('id')}`\n🔗 **Link:** {result.get('htmlLink')}"
            }
            
        except Exception as e:
            logger.error(f"Create event error: {e}")
            return {
                'success': False,
                'message': f"❌ Error creating event: {str(e)}"
            }
    
    def read_events(self, date=None, days=7):
        """
        READ - Get events
        
        Args:
            date: Specific date (YYYY-MM-DD) or None for range
            days: Number of days to fetch (if date is None)
        """
        try:
            if date:
                time_min = datetime.strptime(date, "%Y-%m-%d").isoformat() + 'Z'
                time_max = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).isoformat() + 'Z'
            else:
                time_min = datetime.now().isoformat() + 'Z'
                time_max = (datetime.now() + timedelta(days=days)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return {
                    'success': True,
                    'events': [],
                    'message': "📅 No events found for this period."
                }
            
            message = f"📅 **Found {len(events)} event(s):**\n\n"
            for idx, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                
                message += f"**{idx}. {event['summary']}**\n"
                message += f"   🕐 {start_dt.strftime('%Y-%m-%d %H:%M')}\n"
                
                if event.get('description'):
                    desc = event['description'][:100]
                    message += f"   📝 {desc}{'...' if len(event['description']) > 100 else ''}\n"
                
                message += f"   🆔 `{event['id']}`\n\n"
            
            return {
                'success': True,
                'events': events,
                'message': message
            }
            
        except Exception as e:
            logger.error(f"Read events error: {e}")
            return {
                'success': False,
                'message': f"❌ Error reading events: {str(e)}"
            }
    
    def update_event(self, event_id, **kwargs):
        """
        UPDATE - Update event
        
        Args:
            event_id: Event ID
            **kwargs: Fields to update (title, date, time, duration, description)
        """
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'title' in kwargs:
                event['summary'] = kwargs['title']
            
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            
            if 'date' in kwargs and 'time' in kwargs:
                start_datetime = datetime.strptime(
                    f"{kwargs['date']} {kwargs['time']}",
                    "%Y-%m-%d %H:%M"
                )
                event['start']['dateTime'] = start_datetime.isoformat()
                
                if 'duration' in kwargs:
                    end_datetime = start_datetime + timedelta(minutes=kwargs['duration'])
                    event['end']['dateTime'] = end_datetime.isoformat()
            
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'success': True,
                'message': f"✅ **Event updated!**\n\n📝 **Title:** {updated_event['summary']}\n🔗 **Link:** {updated_event.get('htmlLink')}"
            }
            
        except HttpError as error:
            if error.resp.status == 404:
                return {
                    'success': False,
                    'message': f"❌ Event with ID `{event_id}` not found."
                }
            return {
                'success': False,
                'message': f"❌ Error updating event: {str(error)}"
            }
        except Exception as e:
            logger.error(f"Update event error: {e}")
            return {
                'success': False,
                'message': f"❌ Error: {str(e)}"
            }
    
    def delete_event(self, event_id):
        """
        DELETE - Delete event
        
        Args:
            event_id: Event ID
        """
        try:
            # Get event info before deleting
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            event_title = event.get('summary', 'Unknown')
            
            # Delete
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'message': f"🗑️ **Event deleted!**\n\n📝 **Title:** {event_title}\n🆔 **ID:** `{event_id}`"
            }
            
        except HttpError as error:
            if error.resp.status == 404:
                return {
                    'success': False,
                    'message': f"❌ Event with ID `{event_id}` not found."
                }
            return {
                'success': False,
                'message': f"❌ Error deleting event: {str(error)}"
            }
        except Exception as e:
            logger.error(f"Delete event error: {e}")
            return {
                'success': False,
                'message': f"❌ Error: {str(e)}"
            }