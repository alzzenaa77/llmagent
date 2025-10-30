"""
Integration tests for LLM Agent with Function Calling
Tests the full flow: User message -> LLM -> Function Call -> Response
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import json


class TestLLMAgentInitialization:
    """Test LLM Agent initialization"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_without_calendar(self, mock_model_class, mock_configure):
        """Test initialization without calendar tools"""
        from agent.llm_agent import LLMAgent
        
        agent = LLMAgent(
            api_key="test_api_key",
            model_name="gemini-2.0-flash-exp",
            enable_calendar=False
        )
        
        assert agent.api_key == "test_api_key"
        assert agent.model_name == "gemini-2.0-flash-exp"
        assert agent.enable_calendar == False
        assert agent.tools is None
        mock_configure.assert_called_once_with(api_key="test_api_key")
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch('agent.llm_agent.LLMAgent._setup_calendar_tools')
    def test_init_with_calendar(self, mock_setup_tools, mock_model_class, mock_configure):
        """Test initialization with calendar tools enabled"""
        from agent.llm_agent import LLMAgent
        
        mock_setup_tools.return_value = [MagicMock()]
        
        agent = LLMAgent(
            api_key="test_api_key",
            enable_calendar=True
        )
        
        assert agent.enable_calendar == True
        assert agent.tools is not None
        mock_setup_tools.assert_called_once()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_system_prompt_contains_calendar_info(self, mock_model_class, mock_configure):
        """Test system prompt includes calendar info when enabled"""
        from agent.llm_agent import LLMAgent
        
        with patch('agent.llm_agent.LLMAgent._setup_calendar_tools'):
            agent = LLMAgent(api_key="test_key", enable_calendar=True)
            
            assert "calendar" in agent.system_prompt.lower()
            assert "add_calendar_event" in agent.system_prompt
            assert "list_calendar_events" in agent.system_prompt


class TestLLMAgentSimpleChat:
    """Test simple chat without function calling"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_simple_text_response(self, mock_model_class, mock_configure):
        """Test simple text response without function calling"""
        from agent.llm_agent import LLMAgent
        
        # Setup mock
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock response with only text
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "Hello! How can I help you?"
        mock_part.function_call = None
        mock_response.parts = [mock_part]
        mock_response.text = "Hello! How can I help you?"
        mock_chat.send_message.return_value = mock_response
        
        # Test
        agent = LLMAgent(api_key="test_key", enable_calendar=False)
        response = agent.process("user1", "Hello")
        
        assert response == "Hello! How can I help you?"
        mock_chat.send_message.assert_called_once_with("Hello")
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_empty_response_fallback(self, mock_model_class, mock_configure):
        """Test fallback when response is empty"""
        from agent.llm_agent import LLMAgent
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock empty response
        mock_response = MagicMock()
        mock_response.parts = []
        mock_response.text = None
        mock_chat.send_message.return_value = mock_response
        
        agent = LLMAgent(api_key="test_key", enable_calendar=False)
        response = agent.process("user1", "test")
        
        assert "tidak bisa memproses" in response.lower()


class TestLLMAgentFunctionCalling:
    """Test LLM function calling integration"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch('agent.tools.calendar_tools.add_calendar_event')
    def test_add_event_function_call(self, mock_add_event, mock_model_class, mock_configure):
        """Test adding calendar event via function call"""
        from agent.llm_agent import LLMAgent
        
        # Setup model mock
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock first response with function call
        mock_response1 = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "add_calendar_event"
        mock_fc.args = {
            'title': 'Meeting',
            'date': '2025-10-30',
            'time': '14:00',
            'duration': 60
        }
        
        mock_part1 = MagicMock()
        mock_part1.function_call = mock_fc
        mock_part1.text = None
        mock_response1.parts = [mock_part1]
        
        # Mock second response after function execution
        mock_response2 = MagicMock()
        mock_part2 = MagicMock()
        mock_part2.text = "✅ Event created successfully!"
        mock_part2.function_call = None
        mock_response2.parts = [mock_part2]
        mock_response2.text = "✅ Event created successfully!"
        
        mock_chat.send_message.side_effect = [mock_response1, mock_response2]
        
        # Mock calendar tool response
        mock_add_event.return_value = {
            'success': True,
            'event_id': 'test123',
            'message': 'Event created'
        }
        
        # Test with calendar tools
        with patch('agent.llm_agent.LLMAgent._setup_calendar_tools'):
            agent = LLMAgent(api_key="test_key", enable_calendar=True)
            response = agent.process("user1", "tambahkan meeting besok jam 2")
        
        assert "✅" in response
        mock_add_event.assert_called_once()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch('agent.tools.calendar_tools.list_calendar_events')
    def test_list_events_function_call(self, mock_list_events, mock_model_class, mock_configure):
        """Test listing calendar events via function call"""
        from agent.llm_agent import LLMAgent
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock function call response
        mock_response1 = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "list_calendar_events"
        mock_fc.args = {'days': 7}
        
        mock_part1 = MagicMock()
        mock_part1.function_call = mock_fc
        mock_part1.text = None
        mock_response1.parts = [mock_part1]
        
        # Mock final response
        mock_response2 = MagicMock()
        mock_part2 = MagicMock()
        mock_part2.text = "Kamu punya 2 events minggu ini"
        mock_part2.function_call = None
        mock_response2.parts = [mock_part2]
        mock_response2.text = "Kamu punya 2 events minggu ini"
        
        mock_chat.send_message.side_effect = [mock_response1, mock_response2]
        
        # Mock calendar response
        mock_list_events.return_value = {
            'success': True,
            'events': [
                {'id': 'e1', 'title': 'Event 1'},
                {'id': 'e2', 'title': 'Event 2'}
            ],
            'message': 'Found 2 events'
        }
        
        with patch('agent.llm_agent.LLMAgent._setup_calendar_tools'):
            agent = LLMAgent(api_key="test_key", enable_calendar=True)
            response = agent.process("user1", "apa jadwalku?")
        
        assert "events" in response.lower() or "2" in response
        mock_list_events.assert_called_once()


class TestLLMAgentErrorHandling:
    """Test error handling in function calls"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch('agent.tools.calendar_tools.add_calendar_event')
    def test_function_execution_error(self, mock_add_event, mock_model_class, mock_configure):
        """Test handling of function execution errors"""
        from agent.llm_agent import LLMAgent
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock function call
        mock_response1 = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "add_calendar_event"
        mock_fc.args = {'title': 'Test', 'date': '2025-10-30', 'time': '14:00'}
        
        mock_part1 = MagicMock()
        mock_part1.function_call = mock_fc
        mock_part1.text = None
        mock_response1.parts = [mock_part1]
        
        # Mock error response
        mock_response2 = MagicMock()
        mock_part2 = MagicMock()
        mock_part2.text = "Maaf, terjadi error"
        mock_part2.function_call = None
        mock_response2.parts = [mock_part2]
        mock_response2.text = "Maaf, terjadi error"
        
        mock_chat.send_message.side_effect = [mock_response1, mock_response2]
        
        # Mock function error
        mock_add_event.return_value = {
            'success': False,
            'message': 'API Error'
        }
        
        with patch('agent.llm_agent.LLMAgent._setup_calendar_tools'):
            agent = LLMAgent(api_key="test_key", enable_calendar=True)
            response = agent.process("user1", "tambah event")
        
        assert "error" in response.lower() or "maaf" in response.lower()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_process_exception_handling(self, mock_model_class, mock_configure):
        """Test exception handling in process method"""
        from agent.llm_agent import LLMAgent
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock exception
        mock_chat.send_message.side_effect = Exception("Network error")
        
        agent = LLMAgent(api_key="test_key", enable_calendar=False)
        response = agent.process("user1", "test")
        
        assert "Error" in response


class TestLLMAgentConversation:
    """Test conversation management"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_multi_turn_conversation(self, mock_model_class, mock_configure):
        """Test that conversation history is maintained"""
        from agent.llm_agent import LLMAgent
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        
        # Mock responses
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "Response"
        mock_part.function_call = None
        mock_response.parts = [mock_part]
        mock_response.text = "Response"
        mock_chat.send_message.return_value = mock_response
        
        agent = LLMAgent(api_key="test_key", enable_calendar=False)
        
        # First message
        agent.process("user1", "Hello")
        assert "user1" in agent.chat_sessions
        
        # Second message - should use same chat session
        agent.process("user1", "How are you?")
        assert mock_chat.send_message.call_count == 2
        
        # Different user - should create new session
        agent.process("user2", "Hi")
        assert "user2" in agent.chat_sessions
        assert len(agent.chat_sessions) == 2
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_clear_history(self, mock_model_class, mock_configure):
        """Test clearing conversation history"""
        from agent.llm_agent import LLMAgent
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        agent = LLMAgent(api_key="test_key", enable_calendar=False)
        agent.chat_sessions['user1'] = MagicMock()
        
        result = agent.clear_history('user1')
        
        assert "user1" not in agent.chat_sessions
        assert "cleared" in result.lower()


class TestLLMAgentUtilities:
    """Test utility methods"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_get_help(self, mock_model_class, mock_configure):
        """Test get_help method"""
        from agent.llm_agent import LLMAgent
        
        agent = LLMAgent(api_key="test_key", enable_calendar=False)
        help_text = agent.get_help()
        
        assert "help" in help_text.lower() or "bot" in help_text.lower()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_get_stats(self, mock_model_class, mock_configure):
        """Test get_stats method"""
        from agent.llm_agent import LLMAgent
        
        agent = LLMAgent(api_key="test_key", enable_calendar=True)
        agent.chat_sessions = {'user1': MagicMock(), 'user2': MagicMock()}
        
        stats = agent.get_stats()
        
        assert "2" in stats  # Active users count
        assert "gemini" in stats.lower()


class TestCalendarToolsIntegration:
    """Test CALENDAR_TOOLS integration with LLM"""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_tools_loaded_correctly(self, mock_model_class, mock_configure):
        """Test that calendar tools are loaded correctly"""
        from agent.llm_agent import LLMAgent
        from agent.tools.calendar_tools import CALENDAR_TOOLS
        
        with patch('agent.llm_agent.LLMAgent._setup_calendar_tools') as mock_setup:
            mock_tools = [MagicMock()]
            mock_setup.return_value = mock_tools
            
            agent = LLMAgent(api_key="test_key", enable_calendar=True)
            
            assert agent.tools == mock_tools
            mock_setup.assert_called_once()
    
    def test_calendar_tools_have_required_fields(self):
        """Test that CALENDAR_TOOLS have all required fields"""
        from agent.tools.calendar_tools import CALENDAR_TOOLS
        
        required_fields = ['name', 'description', 'parameters']
        
        for tool in CALENDAR_TOOLS:
            for field in required_fields:
                assert field in tool, f"Tool {tool.get('name')} missing {field}"