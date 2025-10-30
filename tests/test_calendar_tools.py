"""
Unit tests for calendar_tools wrapper functions
"""
import pytest
from unittest.mock import patch, MagicMock


class TestAddCalendarEvent:
    """Test add_calendar_event function"""
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_add_event_success(self, mock_get_agent, sample_event_data):
        """Test adding event successfully"""
        from agent.tools.calendar_tools import add_calendar_event
        
        # Mock agent response
        mock_agent = MagicMock()
        mock_agent.create_event.return_value = {
            'success': True,
            'event_id': 'test123',
            'message': 'Event created'
        }
        mock_get_agent.return_value = mock_agent
        
        result = add_calendar_event(**sample_event_data)
        
        assert result['success'] == True
        assert 'event_id' in result
        mock_agent.create_event.assert_called_once()
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_add_event_with_optional_params(self, mock_get_agent):
        """Test adding event with all optional parameters"""
        from agent.tools.calendar_tools import add_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.create_event.return_value = {'success': True, 'event_id': 'test123'}
        mock_get_agent.return_value = mock_agent
        
        result = add_calendar_event(
            title='Meeting',
            date='2025-10-30',
            time='14:00',
            duration=90,
            description='Important meeting'
        )
        
        assert result['success'] == True
        # Verify all params were passed
        call_args = mock_agent.create_event.call_args
        assert call_args.kwargs['duration'] == 90
        assert call_args.kwargs['description'] == 'Important meeting'
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_add_event_error_handling(self, mock_get_agent):
        """Test error handling when agent fails"""
        from agent.tools.calendar_tools import add_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.create_event.side_effect = Exception("Calendar API Error")
        mock_get_agent.return_value = mock_agent
        
        result = add_calendar_event(
            title='Test',
            date='2025-10-30',
            time='14:00'
        )
        
        assert result['success'] == False
        assert 'Error' in result['message']


class TestListCalendarEvents:
    """Test list_calendar_events function"""
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_list_events_default(self, mock_get_agent):
        """Test listing events with default parameters"""
        from agent.tools.calendar_tools import list_calendar_events
        
        mock_agent = MagicMock()
        mock_agent.read_events.return_value = {
            'success': True,
            'events': [{'id': 'e1', 'title': 'Event 1'}],
            'message': 'Found 1 event'
        }
        mock_get_agent.return_value = mock_agent
        
        result = list_calendar_events()
        
        assert result['success'] == True
        assert len(result['events']) == 1
        # Should call with default days=7
        mock_agent.read_events.assert_called_once_with(date=None, days=7)
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_list_events_specific_date(self, mock_get_agent):
        """Test listing events for specific date"""
        from agent.tools.calendar_tools import list_calendar_events
        
        mock_agent = MagicMock()
        mock_agent.read_events.return_value = {
            'success': True,
            'events': [],
            'message': 'No events'
        }
        mock_get_agent.return_value = mock_agent
        
        result = list_calendar_events(date='2025-10-30')
        
        assert result['success'] == True
        mock_agent.read_events.assert_called_once_with(date='2025-10-30', days=7)
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_list_events_custom_days(self, mock_get_agent):
        """Test listing events for custom number of days"""
        from agent.tools.calendar_tools import list_calendar_events
        
        mock_agent = MagicMock()
        mock_agent.read_events.return_value = {'success': True, 'events': []}
        mock_get_agent.return_value = mock_agent
        
        result = list_calendar_events(days=14)
        
        mock_agent.read_events.assert_called_once_with(date=None, days=14)
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_list_events_error(self, mock_get_agent):
        """Test error handling when listing fails"""
        from agent.tools.calendar_tools import list_calendar_events
        
        mock_agent = MagicMock()
        mock_agent.read_events.side_effect = Exception("Network error")
        mock_get_agent.return_value = mock_agent
        
        result = list_calendar_events()
        
        assert result['success'] == False
        assert 'Error' in result['message']


class TestUpdateCalendarEvent:
    """Test update_calendar_event function"""
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_update_event_title_only(self, mock_get_agent):
        """Test updating only title"""
        from agent.tools.calendar_tools import update_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.update_event.return_value = {'success': True, 'message': 'Updated'}
        mock_get_agent.return_value = mock_agent
        
        result = update_calendar_event(
            event_id='test123',
            title='New Title'
        )
        
        assert result['success'] == True
        # Should only pass title
        call_kwargs = mock_agent.update_event.call_args.kwargs
        assert 'title' in call_kwargs
        assert call_kwargs['title'] == 'New Title'
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_update_event_multiple_fields(self, mock_get_agent):
        """Test updating multiple fields"""
        from agent.tools.calendar_tools import update_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.update_event.return_value = {'success': True}
        mock_get_agent.return_value = mock_agent
        
        result = update_calendar_event(
            event_id='test123',
            title='New Title',
            date='2025-11-01',
            time='15:00',
            duration=120
        )
        
        assert result['success'] == True
        call_kwargs = mock_agent.update_event.call_args.kwargs
        assert call_kwargs['title'] == 'New Title'
        assert call_kwargs['date'] == '2025-11-01'
        assert call_kwargs['time'] == '15:00'
        assert call_kwargs['duration'] == 120
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_update_event_none_values_ignored(self, mock_get_agent):
        """Test that None values are not passed to agent"""
        from agent.tools.calendar_tools import update_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.update_event.return_value = {'success': True}
        mock_get_agent.return_value = mock_agent
        
        result = update_calendar_event(
            event_id='test123',
            title='New Title',
            date=None,  # Should not be passed
            time=None   # Should not be passed
        )
        
        call_kwargs = mock_agent.update_event.call_args.kwargs
        assert 'title' in call_kwargs
        assert 'date' not in call_kwargs
        assert 'time' not in call_kwargs
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_update_event_error(self, mock_get_agent):
        """Test error handling during update"""
        from agent.tools.calendar_tools import update_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.update_event.side_effect = Exception("Update failed")
        mock_get_agent.return_value = mock_agent
        
        result = update_calendar_event(event_id='test123', title='New')
        
        assert result['success'] == False
        assert 'Error' in result['message']


class TestDeleteCalendarEvent:
    """Test delete_calendar_event function"""
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_delete_event_success(self, mock_get_agent):
        """Test deleting event successfully"""
        from agent.tools.calendar_tools import delete_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.delete_event.return_value = {
            'success': True,
            'message': 'Event deleted'
        }
        mock_get_agent.return_value = mock_agent
        
        result = delete_calendar_event(event_id='test123')
        
        assert result['success'] == True
        mock_agent.delete_event.assert_called_once_with(event_id='test123')
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_delete_event_not_found(self, mock_get_agent):
        """Test deleting non-existent event"""
        from agent.tools.calendar_tools import delete_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.delete_event.return_value = {
            'success': False,
            'message': 'Event not found'
        }
        mock_get_agent.return_value = mock_agent
        
        result = delete_calendar_event(event_id='nonexistent')
        
        assert result['success'] == False
        assert 'not found' in result['message'].lower()
    
    @patch('agent.tools.calendar_tools.get_calendar_agent')
    def test_delete_event_error(self, mock_get_agent):
        """Test error handling during delete"""
        from agent.tools.calendar_tools import delete_calendar_event
        
        mock_agent = MagicMock()
        mock_agent.delete_event.side_effect = Exception("Delete failed")
        mock_get_agent.return_value = mock_agent
        
        result = delete_calendar_event(event_id='test123')
        
        assert result['success'] == False
        assert 'Error' in result['message']


class TestCalendarToolsDeclarations:
    """Test CALENDAR_TOOLS declarations"""
    
    def test_tools_structure(self):
        """Test that CALENDAR_TOOLS has correct structure"""
        from agent.tools.calendar_tools import CALENDAR_TOOLS
        
        assert isinstance(CALENDAR_TOOLS, list)
        assert len(CALENDAR_TOOLS) == 4  # 4 CRUD operations
        
        for tool in CALENDAR_TOOLS:
            assert 'name' in tool
            assert 'description' in tool
            assert 'parameters' in tool
    
    def test_required_tools_exist(self):
        """Test all 4 CRUD tools are declared"""
        from agent.tools.calendar_tools import CALENDAR_TOOLS
        
        tool_names = [tool['name'] for tool in CALENDAR_TOOLS]
        
        assert 'add_calendar_event' in tool_names
        assert 'list_calendar_events' in tool_names
        assert 'update_calendar_event' in tool_names
        assert 'delete_calendar_event' in tool_names
    
    def test_tool_parameters_structure(self):
        """Test each tool has proper parameter structure"""
        from agent.tools.calendar_tools import CALENDAR_TOOLS
        
        for tool in CALENDAR_TOOLS:
            params = tool['parameters']
            assert 'type' in params
            assert params['type'] == 'object'
            assert 'properties' in params
            assert isinstance(params['properties'], dict)