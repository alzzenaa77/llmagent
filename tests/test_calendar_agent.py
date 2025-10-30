"""
Unit tests for CalendarAgent CRUD operations
"""
import pytest
from unittest.mock import patch, MagicMock
from googleapiclient.errors import HttpError


class TestCalendarAgentCreate:
    """Test CREATE operations"""
    
    def test_create_event_success(self, mock_calendar_agent, sample_event_data):
        """Test creating event successfully"""
        result = mock_calendar_agent.create_event(**sample_event_data)
        
        assert result['success'] == True
        assert 'event_id' in result
        assert result['event_id'] == 'test_event_123'
        assert 'link' in result
        assert 'Test Meeting' in result['message']
    
    def test_create_event_with_default_duration(self, mock_calendar_agent):
        """Test creating event with default duration"""
        result = mock_calendar_agent.create_event(
            title='Quick Meeting',
            date='2025-10-30',
            time='10:00'
            # duration not provided, should default to 60
        )
        
        assert result['success'] == True
        assert '60 minutes' in result['message']
    
    def test_create_event_with_description(self, mock_calendar_agent):
        """Test creating event with description"""
        result = mock_calendar_agent.create_event(
            title='Important Meeting',
            date='2025-10-30',
            time='14:00',
            duration=90,
            description='Discuss project roadmap'
        )
        
        assert result['success'] == True
        assert result['event_id'] == 'test_event_123'
    
    def test_create_event_invalid_date_format(self, mock_calendar_agent):
        """Test creating event with invalid date format"""
        result = mock_calendar_agent.create_event(
            title='Bad Date Event',
            date='30-10-2025',  # Wrong format
            time='14:00'
        )
        
        assert result['success'] == False
        assert 'Error' in result['message']
    
    def test_create_event_invalid_time_format(self, mock_calendar_agent):
        """Test creating event with invalid time format"""
        result = mock_calendar_agent.create_event(
            title='Bad Time Event',
            date='2025-10-30',
            time='2:00 PM'  # Wrong format
        )
        
        assert result['success'] == False
        assert 'Error' in result['message']


class TestCalendarAgentRead:
    """Test READ operations"""
    
    def test_read_events_success(self, mock_calendar_agent):
        """Test reading events successfully"""
        result = mock_calendar_agent.read_events(days=7)
        
        assert result['success'] == True
        assert 'events' in result
        assert len(result['events']) > 0
        assert 'Found' in result['message']
    
    def test_read_events_specific_date(self, mock_calendar_agent):
        """Test reading events for specific date"""
        result = mock_calendar_agent.read_events(date='2025-10-30')
        
        assert result['success'] == True
        assert 'events' in result
    
    def test_read_events_no_events(self, mock_calendar_agent):
        """Test reading when no events exist"""
        # Mock empty response
        mock_calendar_agent.service.events().list().execute.return_value = {'items': []}
        
        result = mock_calendar_agent.read_events(days=7)
        
        assert result['success'] == True
        assert len(result['events']) == 0
        assert 'No events found' in result['message']
    
    def test_read_events_with_description(self, mock_calendar_agent, sample_events_list):
        """Test reading events that have descriptions"""
        mock_calendar_agent.service.events().list().execute.return_value = sample_events_list
        
        result = mock_calendar_agent.read_events(days=7)
        
        assert result['success'] == True
        assert len(result['events']) == 2
        # Check that description is included in message
        assert 'Team sync' in result['message'] or 'Morning Meeting' in result['message']


class TestCalendarAgentUpdate:
    """Test UPDATE operations"""
    
    def test_update_event_title(self, mock_calendar_agent):
        """Test updating event title"""
        result = mock_calendar_agent.update_event(
            event_id='test_event_123',
            title='Updated Meeting Title'
        )
        
        assert result['success'] == True
        assert 'updated' in result['message'].lower()
    
    def test_update_event_description(self, mock_calendar_agent):
        """Test updating event description"""
        result = mock_calendar_agent.update_event(
            event_id='test_event_123',
            description='New description'
        )
        
        assert result['success'] == True
    
    def test_update_event_datetime(self, mock_calendar_agent):
        """Test updating event date and time"""
        result = mock_calendar_agent.update_event(
            event_id='test_event_123',
            date='2025-11-01',
            time='15:00',
            duration=120
        )
        
        assert result['success'] == True
    
    def test_update_event_not_found(self, mock_calendar_agent):
        """Test updating non-existent event"""
        # Mock 404 error
        mock_error = HttpError(
            resp=MagicMock(status=404),
            content=b'Not Found'
        )
        mock_calendar_agent.service.events().get.side_effect = mock_error
        
        result = mock_calendar_agent.update_event(
            event_id='nonexistent_id',
            title='New Title'
        )
        
        assert result['success'] == False
        assert 'not found' in result['message'].lower()
    
    def test_update_event_multiple_fields(self, mock_calendar_agent):
        """Test updating multiple fields at once"""
        result = mock_calendar_agent.update_event(
            event_id='test_event_123',
            title='Completely New Meeting',
            description='Completely new description',
            date='2025-11-15',
            time='10:00',
            duration=90
        )
        
        assert result['success'] == True


class TestCalendarAgentDelete:
    """Test DELETE operations"""
    
    def test_delete_event_success(self, mock_calendar_agent):
        """Test deleting event successfully"""
        result = mock_calendar_agent.delete_event(event_id='test_event_123')
        
        assert result['success'] == True
        assert 'deleted' in result['message'].lower()
        assert 'test_event_123' in result['message']
    
    def test_delete_event_not_found(self, mock_calendar_agent):
        """Test deleting non-existent event"""
        # Mock 404 error
        mock_error = HttpError(
            resp=MagicMock(status=404),
            content=b'Not Found'
        )
        mock_calendar_agent.service.events().get.side_effect = mock_error
        
        result = mock_calendar_agent.delete_event(event_id='nonexistent_id')
        
        assert result['success'] == False
        assert 'not found' in result['message'].lower()
    
    def test_delete_event_shows_title(self, mock_calendar_agent):
        """Test that delete confirmation shows event title"""
        result = mock_calendar_agent.delete_event(event_id='test_event_123')
        
        assert result['success'] == True
        # Should show the title of deleted event
        assert 'Test Meeting' in result['message']


class TestCalendarAgentErrors:
    """Test error handling"""
    
    def test_create_event_api_error(self, mock_calendar_agent):
        """Test handling API error during create"""
        mock_calendar_agent.service.events().insert().execute.side_effect = Exception("API Error")
        
        result = mock_calendar_agent.create_event(
            title='Test',
            date='2025-10-30',
            time='14:00'
        )
        
        assert result['success'] == False
        assert 'Error' in result['message']
    
    def test_read_events_api_error(self, mock_calendar_agent):
        """Test handling API error during read"""
        mock_calendar_agent.service.events().list().execute.side_effect = Exception("API Error")
        
        result = mock_calendar_agent.read_events(days=7)
        
        assert result['success'] == False
        assert 'Error' in result['message']
    
    def test_update_event_generic_error(self, mock_calendar_agent):
        """Test handling generic error during update"""
        mock_calendar_agent.service.events().get.side_effect = Exception("Network Error")
        
        result = mock_calendar_agent.update_event(
            event_id='test123',
            title='New Title'
        )
        
        assert result['success'] == False
        assert 'Error' in result['message']