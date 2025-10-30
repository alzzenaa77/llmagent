"""
Pytest fixtures for testing SchedBot
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ==========================================
# MOCK DATA
# ==========================================

@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        'title': 'Test Meeting',
        'date': '2025-10-30',
        'time': '14:00',
        'duration': 60,
        'description': 'Test description'
    }


@pytest.fixture
def sample_calendar_api_response():
    """Mock Google Calendar API response"""
    return {
        'id': 'test_event_123',
        'summary': 'Test Meeting',
        'description': 'Test description',
        'start': {
            'dateTime': '2025-10-30T14:00:00+07:00',
            'timeZone': 'Asia/Jakarta'
        },
        'end': {
            'dateTime': '2025-10-30T15:00:00+07:00',
            'timeZone': 'Asia/Jakarta'
        },
        'htmlLink': 'https://calendar.google.com/event?eid=test123'
    }


@pytest.fixture
def sample_events_list():
    """Mock list of events from Calendar API"""
    return {
        'items': [
            {
                'id': 'event1',
                'summary': 'Morning Meeting',
                'start': {'dateTime': '2025-10-30T09:00:00+07:00'},
                'end': {'dateTime': '2025-10-30T10:00:00+07:00'},
                'description': 'Team sync'
            },
            {
                'id': 'event2',
                'summary': 'Lunch Break',
                'start': {'dateTime': '2025-10-30T12:00:00+07:00'},
                'end': {'dateTime': '2025-10-30T13:00:00+07:00'},
                'description': ''
            }
        ]
    }


# ==========================================
# CALENDAR AGENT MOCKS
# ==========================================

@pytest.fixture
def mock_calendar_service():
    """Mock Google Calendar API service"""
    mock_service = MagicMock()
    
    # Mock events().insert()
    mock_insert = MagicMock()
    mock_insert.execute.return_value = {
        'id': 'test_event_123',
        'summary': 'Test Meeting',
        'htmlLink': 'https://calendar.google.com/event?eid=test123'
    }
    mock_service.events().insert.return_value = mock_insert
    
    # Mock events().list()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        'items': [
            {
                'id': 'event1',
                'summary': 'Test Event',
                'start': {'dateTime': '2025-10-30T14:00:00+07:00'},
                'end': {'dateTime': '2025-10-30T15:00:00+07:00'}
            }
        ]
    }
    mock_service.events().list.return_value = mock_list
    
    # Mock events().get()
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        'id': 'test_event_123',
        'summary': 'Test Meeting',
        'description': 'Original description',
        'start': {'dateTime': '2025-10-30T14:00:00+07:00'},
        'end': {'dateTime': '2025-10-30T15:00:00+07:00'}
    }
    mock_service.events().get.return_value = mock_get
    
    # Mock events().update()
    mock_update = MagicMock()
    mock_update.execute.return_value = {
        'summary': 'Updated Meeting',
        'htmlLink': 'https://calendar.google.com/event?eid=test123'
    }
    mock_service.events().update.return_value = mock_update
    
    # Mock events().delete()
    mock_delete = MagicMock()
    mock_delete.execute.return_value = {}
    mock_service.events().delete.return_value = mock_delete
    
    return mock_service


@pytest.fixture
def mock_calendar_agent(mock_calendar_service):
    """Mock CalendarAgent with mocked service"""
    with patch('agent.calendar_agent.build') as mock_build:
        mock_build.return_value = mock_calendar_service
        
        with patch('os.path.exists', return_value=True):
            with patch('agent.calendar_agent.Credentials'):
                from agent.calendar_agent import CalendarAgent
                
                agent = CalendarAgent(
                    credentials_path='test_credentials.json',
                    token_path='test_token.json',
                    timezone='Asia/Jakarta'
                )
                agent.service = mock_calendar_service
                
                yield agent


# ==========================================
# LLM AGENT MOCKS
# ==========================================

@pytest.fixture
def mock_gemini_model():
    """Mock Gemini GenerativeModel"""
    mock_model = MagicMock()
    
    # Mock chat session
    mock_chat = MagicMock()
    mock_response = MagicMock()
    
    # Mock text response (no function call)
    mock_part = MagicMock()
    mock_part.text = "This is a test response"
    mock_part.function_call = None
    mock_response.parts = [mock_part]
    mock_response.text = "This is a test response"
    
    mock_chat.send_message.return_value = mock_response
    mock_model.start_chat.return_value = mock_chat
    
    return mock_model


@pytest.fixture
def mock_llm_agent(mock_gemini_model):
    """Mock LLMAgent"""
    with patch('google.generativeai.configure'):
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model_class.return_value = mock_gemini_model
            
            from agent.llm_agent import LLMAgent
            
            agent = LLMAgent(
                api_key="test_api_key",
                model_name="gemini-1.5-pro",
                enable_calendar=False
            )
            agent.model = mock_gemini_model
            
            yield agent


@pytest.fixture
def mock_function_call_response():
    """Mock Gemini response with function call"""
    mock_response = MagicMock()
    mock_part = MagicMock()
    
    # Mock function_call
    mock_fc = MagicMock()
    mock_fc.name = "add_calendar_event"
    mock_fc.args = {
        'title': 'Test Meeting',
        'date': '2025-10-30',
        'time': '14:00',
        'duration': 60
    }
    
    mock_part.function_call = mock_fc
    mock_part.text = None
    mock_response.parts = [mock_part]
    
    return mock_response


# ==========================================
# CALENDAR TOOLS MOCKS
# ==========================================

@pytest.fixture
def mock_calendar_tools_agent(mock_calendar_service):
    """Mock calendar_tools module's global agent"""
    with patch('agent.calendar_agent.build') as mock_build:
        mock_build.return_value = mock_calendar_service
        
        with patch('os.path.exists', return_value=True):
            with patch('agent.calendar_agent.Credentials'):
                from agent.tools import calendar_tools
                
                # Initialize the global agent
                agent = calendar_tools.init_calendar_agent(
                    credentials_path='test_cred.json',
                    token_path='test_token.json'
                )
                agent.service = mock_calendar_service
                
                yield calendar_tools
