"""
Calendar Tools Module
Wrapper functions for CalendarAgent to be used by LLM Agent
"""

from agent.calendar_agent import CalendarAgent
import logging

logger = logging.getLogger(__name__)

# Global calendar agent instance
_calendar_agent = None

import os

def initialize_calendar_agent(credentials_path=None,
                              token_path=None,
                              timezone='Asia/Jakarta'):
    """
    Initialize calendar agent (call once at startup)
    
    Args:
        credentials_path: Path to credentials.json (default: root/credentials.json)
        token_path: Path to token.json (default: root/token.json)
        timezone: Timezone for events
    """
    global _calendar_agent
    
    # Use absolute paths if not provided
    if credentials_path is None:
        credentials_path = os.path.abspath('credentials.json')
    if token_path is None:
        token_path = os.path.abspath('token.json')
    
    try:
        _calendar_agent = CalendarAgent(
            credentials_path=credentials_path,
            token_path=token_path,
            timezone=timezone
        )
        logger.info("✅ Calendar tools initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize calendar tools: {e}")
        return False

def get_calendar_agent():
    """Get calendar agent instance"""
    if _calendar_agent is None:
        raise RuntimeError("Calendar agent not initialized. Call initialize_calendar_agent() first.")
    return _calendar_agent

# =====================================================
# TOOL FUNCTIONS (untuk dipanggil Gemini)
# =====================================================

def add_calendar_event(title: str, date: str, time: str, 
                       duration: int = 60, description: str = "") -> dict:
    """
    Add event to Google Calendar
    
    This function is designed to be called by Gemini AI via function calling.
    
    Args:
        title: Event title/summary
        date: Date in format YYYY-MM-DD (e.g., "2025-10-28")
        time: Time in format HH:MM (e.g., "14:00")
        duration: Duration in minutes (default: 60)
        description: Event description (optional)
    
    Returns:
        dict: Result with keys:
            - success: bool
            - message: str (formatted message)
            - event_id: str (if success)
            - link: str (if success)
    
    Example:
        >>> result = add_calendar_event("Meeting", "2025-10-28", "14:00", 60)
        >>> print(result['message'])
    """
    try:
        agent = get_calendar_agent()
        result = agent.create_event(
            title=title,
            date=date,
            time=time,
            duration=duration,
            description=description
        )
        
        logger.info(f"✅ Calendar event added: {title}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to add calendar event: {e}")
        return {
            'success': False,
            'message': f"❌ Error adding event: {str(e)}"
        }


def list_calendar_events(date: str = None, days: int = 7) -> dict:
    """
    List events from Google Calendar
    
    This function is designed to be called by Gemini AI via function calling.
    
    Args:
        date: Specific date in YYYY-MM-DD format (optional)
              If provided, shows events for that day only
              If None, shows events for next 'days' days
        days: Number of days ahead to fetch events (default: 7)
              Only used if date is None
    
    Returns:
        dict: Result with keys:
            - success: bool
            - message: str (formatted list of events)
            - events: list (raw event data)
            - count: int (number of events)
    
    Example:
        >>> result = list_calendar_events(days=7)
        >>> print(result['message'])
    """
    try:
        agent = get_calendar_agent()
        result = agent.read_events(date=date, days=days)
        
        logger.info(f"✅ Listed {result.get('count', 0)} calendar events")
        return result
        
    except Exception as e:
        logger.error(f"Failed to list calendar events: {e}")
        return {
            'success': False,
            'message': f"❌ Error listing events: {str(e)}",
            'events': [],
            'count': 0
        }


def delete_calendar_event(event_id: str) -> dict:
    """
    Delete event from Google Calendar
    
    This function is designed to be called by Gemini AI via function calling.
    
    Args:
        event_id: Google Calendar event ID
    
    Returns:
        dict: Result with keys:
            - success: bool
            - message: str (confirmation or error message)
    
    Example:
        >>> result = delete_calendar_event("abc123xyz")
        >>> print(result['message'])
    """
    try:
        agent = get_calendar_agent()
        result = agent.delete_event(event_id=event_id)
        
        logger.info(f"✅ Calendar event deleted: {event_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to delete calendar event: {e}")
        return {
            'success': False,
            'message': f"❌ Error deleting event: {str(e)}"
        }


def update_calendar_event(event_id: str, title: str = None, 
                         date: str = None, time: str = None,
                         duration: int = None, description: str = None) -> dict:
    """
    Update event in Google Calendar
    
    This function is designed to be called by Gemini AI via function calling.
    
    Args:
        event_id: Event ID to update
        title: New title (optional)
        date: New date in YYYY-MM-DD (optional)
        time: New time in HH:MM (optional)
        duration: New duration in minutes (optional)
        description: New description (optional)
    
    Returns:
        dict: Result with keys:
            - success: bool
            - message: str (confirmation or error message)
    
    Example:
        >>> result = update_calendar_event("abc123", title="New Title")
        >>> print(result['message'])
    """
    try:
        agent = get_calendar_agent()
        
        # Build update kwargs (only non-None values)
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
        
        result = agent.update_event(event_id=event_id, **update_kwargs)
        
        logger.info(f"✅ Calendar event updated: {event_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to update calendar event: {e}")
        return {
            'success': False,
            'message': f"❌ Error updating event: {str(e)}"
        }


# =====================================================
# TOOL DEFINITIONS (untuk Gemini Function Calling)
# =====================================================

CALENDAR_TOOLS = [
    {
        "name": "add_calendar_event",
        "description": """Add a new event to user's Google Calendar. 
Use this when user wants to schedule, create, or add an event/meeting/appointment.
Examples: "jadwalin meeting besok", "buatkan reminder olahraga", "schedule interview".""",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Event title/summary. Be descriptive but concise."
                },
                "date": {
                    "type": "string",
                    "description": "Event date in YYYY-MM-DD format. Calculate from relative dates like 'besok', 'minggu depan', etc."
                },
                "time": {
                    "type": "string",
                    "description": "Event start time in HH:MM format (24-hour). Convert keywords: 'pagi'=09:00, 'siang'=12:00, 'sore'=15:00, 'malam'=19:00"
                },
                "duration": {
                    "type": "integer",
                    "description": "Event duration in minutes. Default: 60. Convert hours to minutes (1 jam = 60 menit)."
                },
                "description": {
                    "type": "string",
                    "description": "Optional event description or notes."
                }
            },
            "required": ["title", "date", "time"]
        }
    },
    {
        "name": "list_calendar_events",
        "description": """List upcoming events from user's Google Calendar.
Use this when user wants to see, check, or view their schedule/agenda.
Examples: "apa jadwalku hari ini?", "tampilkan agenda minggu ini", "list my events".""",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Specific date in YYYY-MM-DD format to show events for that day only. Leave null for range."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days ahead to fetch events (used if date is null). Default: 7"
                }
            },
            "required": []
        }
    },
    {
        "name": "delete_calendar_event",
        "description": """Delete an event from user's Google Calendar.
Use this when user wants to remove, cancel, or delete an event.
You MUST get the event_id first by calling list_calendar_events if user doesn't provide it.
Examples: "hapus meeting hari ini", "cancel event abc123", "batalkan janji".""",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "Google Calendar event ID. Get this from list_calendar_events first if not provided by user."
                }
            },
            "required": ["event_id"]
        }
    },
    {
        "name": "update_calendar_event",
        "description": """Update an existing event in user's Google Calendar.
Use this when user wants to modify, change, or reschedule an event.
You MUST get the event_id first by calling list_calendar_events if user doesn't provide it.
Examples: "ubah meeting jadi besok", "reschedule to 3pm", "ganti judulnya".""",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "Google Calendar event ID. Get this from list_calendar_events first."
                },
                "title": {
                    "type": "string",
                    "description": "New event title (optional)"
                },
                "date": {
                    "type": "string",
                    "description": "New date in YYYY-MM-DD (optional)"
                },
                "time": {
                    "type": "string",
                    "description": "New time in HH:MM (optional)"
                },
                "duration": {
                    "type": "integer",
                    "description": "New duration in minutes (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)"
                }
            },
            "required": ["event_id"]
        }
    }
]