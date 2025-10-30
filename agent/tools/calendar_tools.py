"""
Calendar Tools - Connected to Google Calendar via CalendarAgent
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Global CalendarAgent instance
_calendar_agent = None

def init_calendar_agent(credentials_path='credentials/credentials.json', 
                       token_path='credentials/token.json'):
    """
    Initialize CalendarAgent (call this once at startup)
    """
    global _calendar_agent
    
    if _calendar_agent is None:
        from agent.calendar_agent import CalendarAgent
        _calendar_agent = CalendarAgent(
            credentials_path=credentials_path,
            token_path=token_path,
            timezone='Asia/Jakarta'
        )
        logger.info("✅ CalendarAgent initialized in calendar_tools")
    
    return _calendar_agent

def get_calendar_agent():
    """Get or initialize CalendarAgent"""
    global _calendar_agent
    
    if _calendar_agent is None:
        init_calendar_agent()
    
    return _calendar_agent

# ====================
# TOOL FUNCTIONS
# ====================

def add_calendar_event(title: str, date: str, time: str, 
                       duration: int = 60, description: str = ""):
    """
    Add event to Google Calendar
    
    Args:
        title: Event title
        date: Date in YYYY-MM-DD format (e.g. "2024-12-25")
        time: Time in HH:MM format (e.g. "14:00")
        duration: Duration in minutes (default: 60)
        description: Event description (optional)
    
    Returns:
        dict: Result with success status and message
    """
    try:
        logger.info(f"📝 Creating event: {title} on {date} at {time}")
        
        agent = get_calendar_agent()
        result = agent.create_event(
            title=title,
            date=date,
            time=time,
            duration=duration,
            description=description
        )
        
        logger.info(f"✅ Event created: {result.get('event_id')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error creating event: {e}", exc_info=True)
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

def list_calendar_events(date: str = None, days: int = 7):
    """
    List events from Google Calendar
    
    Args:
        date: Specific date in YYYY-MM-DD format (optional)
              If provided, only shows events on that date
              If None, shows events for next 'days' days
        days: Number of days to fetch (default: 7)
              Only used if date is None
    
    Returns:
        dict: Result with events list and message
    """
    try:
        logger.info(f"📅 Listing events: date={date}, days={days}")
        
        agent = get_calendar_agent()
        result = agent.read_events(date=date, days=days)
        
        logger.info(f"✅ Found {len(result.get('events', []))} events")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error listing events: {e}", exc_info=True)
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

def update_calendar_event(event_id: str, title: str = None, 
                         date: str = None, time: str = None,
                         duration: int = None, description: str = None):
    """
    Update event in Google Calendar
    
    Args:
        event_id: Event ID to update
        title: New title (optional)
        date: New date in YYYY-MM-DD format (optional)
        time: New time in HH:MM format (optional)
        duration: New duration in minutes (optional)
        description: New description (optional)
    
    Returns:
        dict: Result with success status and message
    """
    try:
        logger.info(f"✏️ Updating event: {event_id}")
        
        # Build kwargs for update
        update_kwargs = {}
        if title is not None:
            update_kwargs['title'] = title
        if date is not None:
            update_kwargs['date'] = date
        if time is not None:
            update_kwargs['time'] = time
        if duration is not None:
            update_kwargs['duration'] = duration
        if description is not None:
            update_kwargs['description'] = description
        
        agent = get_calendar_agent()
        result = agent.update_event(event_id=event_id, **update_kwargs)
        
        logger.info(f"✅ Event updated")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error updating event: {e}", exc_info=True)
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

def delete_calendar_event(event_id: str):
    """
    Delete event from Google Calendar
    
    Args:
        event_id: Event ID to delete
    
    Returns:
        dict: Result with success status and message
    """
    try:
        logger.info(f"🗑️ Deleting event: {event_id}")
        
        agent = get_calendar_agent()
        result = agent.delete_event(event_id=event_id)
        
        logger.info(f"✅ Event deleted")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error deleting event: {e}", exc_info=True)
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}"
        }

# ====================
# TOOL DECLARATIONS for Gemini
# ====================

CALENDAR_TOOLS = [
    {
        'name': 'add_calendar_event',
        'description': 'Add a new event to Google Calendar. Use this when user wants to create/add/schedule an event.',
        'parameters': {
            'type': 'object',
            'properties': {
                'title': {
                    'type': 'string',
                    'description': 'Event title/summary'
                },
                'date': {
                    'type': 'string',
                    'description': 'Event date in YYYY-MM-DD format (e.g. "2024-12-25")'
                },
                'time': {
                    'type': 'string',
                    'description': 'Event time in HH:MM format (e.g. "14:00" for 2 PM)'
                },
                'duration': {
                    'type': 'integer',
                    'description': 'Event duration in minutes (default: 60)'
                },
                'description': {
                    'type': 'string',
                    'description': 'Event description/notes (optional)'
                }
            },
            'required': ['title', 'date', 'time']
        }
    },
    {
        'name': 'list_calendar_events',
        'description': 'List events from Google Calendar. Use this when user wants to see/check their schedule.',
        'parameters': {
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'description': 'Specific date in YYYY-MM-DD format. If provided, only shows events on that date. Leave empty to show upcoming events.'
                },
                'days': {
                    'type': 'integer',
                    'description': 'Number of days to fetch (default: 7). Only used if date is not provided.'
                }
            },
            'required': []
        }
    },
    {
        'name': 'update_calendar_event',
        'description': 'Update an existing event in Google Calendar. Use this when user wants to modify/change an event.',
        'parameters': {
            'type': 'object',
            'properties': {
                'event_id': {
                    'type': 'string',
                    'description': 'Event ID to update (get from list_calendar_events)'
                },
                'title': {
                    'type': 'string',
                    'description': 'New title (optional)'
                },
                'date': {
                    'type': 'string',
                    'description': 'New date in YYYY-MM-DD format (optional)'
                },
                'time': {
                    'type': 'string',
                    'description': 'New time in HH:MM format (optional)'
                },
                'duration': {
                    'type': 'integer',
                    'description': 'New duration in minutes (optional)'
                },
                'description': {
                    'type': 'string',
                    'description': 'New description (optional)'
                }
            },
            'required': ['event_id']
        }
    },
    {
        'name': 'delete_calendar_event',
        'description': 'Delete an event from Google Calendar. Use this when user wants to remove/cancel an event.',
        'parameters': {
            'type': 'object',
            'properties': {
                'event_id': {
                    'type': 'string',
                    'description': 'Event ID to delete (get from list_calendar_events)'
                }
            },
            'required': ['event_id']
        }
    }
]