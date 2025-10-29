import os
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class LLMAgent:
    """LLM Agent using Google Gemini with Function Calling"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp", 
                 enable_calendar: bool = False):
        """
        Initialize LLM Agent
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use
            enable_calendar: Enable calendar tools (requires calendar_agent)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.enable_calendar = enable_calendar
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # System prompt with calendar awareness
        self.system_prompt = self._build_system_prompt()
        
        # Setup tools
        self.tools = None
        if self.enable_calendar:
            self.tools = self._setup_calendar_tools()
        
        # Initialize model with tools
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tools,
            system_instruction=self.system_prompt
        )
        
        # Chat history storage
        self.chat_sessions = {}
        
        logger.info(f"✅ LLM Agent initialized (Calendar: {'ON' if enable_calendar else 'OFF'})")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt based on capabilities"""
        
        base_prompt = """Kamu adalah asisten AI yang helpful dan friendly.

PERSONALITY:
- Ramah, santai, tapi profesional
- Gunakan emoji secukupnya (jangan berlebihan)
- Jawab dalam Bahasa Indonesia yang natural

CAPABILITIES:"""
        
        if self.enable_calendar:
            base_prompt += """
- Chat biasa untuk pertanyaan umum
- **Manage Google Calendar** menggunakan tools yang tersedia

CRITICAL: JIKA DETECT CALENDAR REQUEST, LANGSUNG USE TOOL!

CALENDAR KEYWORDS (AUTO TRIGGER TOOL):
- jadwal, schedule, agenda, meeting, rapat, event, acara
- tambah, tambahkan, buatkan, jadwalin, schedule
- apa jadwal, lihat agenda, cek event, tampilkan jadwal
- hapus, cancel, batalkan, ubah, update, reschedule

TOOLS AVAILABLE:
1. add_calendar_event - Create event
2. list_calendar_events - List events  
3. delete_calendar_event - Delete event
4. update_calendar_event - Update event

DATE/TIME RULES:
- "hari ini" = {today}
- "besok" = {tomorrow}
- "lusa" = {day_after_tomorrow}
- "pagi"=09:00, "siang"=12:00, "sore"=15:00, "malam"=19:00
- "jam 2" = 14:00

EXAMPLES:
User: "tambahkan jadwal besok jam 2"
→ USE: add_calendar_event(title="Jadwal", date="{tomorrow}", time="14:00", duration=60)

User: "apa jadwalku hari ini?"
→ USE: list_calendar_events(date="{today}")
"""
        else:
            base_prompt += """
- Chat untuk pertanyaan umum
- Membantu brainstorming
- Memberikan penjelasan dan tips
"""
        
        base_prompt += """

RESPONSE STYLE:
- Natural dan informatif
- Konfirmasi detail setelah execute tool
"""
        
        # Inject dates
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        base_prompt = base_prompt.replace("{today}", today)
        base_prompt = base_prompt.replace("{tomorrow}", tomorrow)
        base_prompt = base_prompt.replace("{day_after_tomorrow}", day_after)
        
        return base_prompt
    
    def _setup_calendar_tools(self) -> list:
        """Setup calendar tools"""
        from agent.tools.calendar_tools import CALENDAR_TOOLS
        
        # Convert to proper format
        tool_declarations = []
        
        for tool_dict in CALENDAR_TOOLS:
            func_decl = genai.protos.FunctionDeclaration(
                name=tool_dict['name'],
                description=tool_dict['description'],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=self._get_proto_type(v.get('type')),
                            description=v.get('description', '')
                        )
                        for k, v in tool_dict['parameters']['properties'].items()
                    },
                    required=tool_dict['parameters'].get('required', [])
                )
            )
            tool_declarations.append(func_decl)
        
        logger.info(f"✅ Loaded {len(tool_declarations)} calendar tools")
        for decl in tool_declarations:
            logger.info(f"   - {decl.name}")
        
        return [genai.protos.Tool(function_declarations=tool_declarations)]
    
    def _get_proto_type(self, type_str: str):
        """Convert JSON schema type to protobuf Type"""
        type_map = {
            'string': genai.protos.Type.STRING,
            'integer': genai.protos.Type.INTEGER,
            'number': genai.protos.Type.NUMBER,
            'boolean': genai.protos.Type.BOOLEAN,
            'array': genai.protos.Type.ARRAY,
            'object': genai.protos.Type.OBJECT
        }
        return type_map.get(type_str, genai.protos.Type.STRING)
    
    def _extract_function_calls_from_raw(self, response):
        """
        Extract function calls from raw response
        This is a workaround for empty name bug
        """
        function_calls = []
        
        try:
            # Try to get raw proto message
            if hasattr(response, '_result'):
                raw = response._result
                logger.info(f"🔍 Raw result type: {type(raw)}")
                
                # Try to serialize to dict
                try:
                    if hasattr(raw, 'to_dict'):
                        raw_dict = raw.to_dict()
                        logger.info(f"🔍 Raw dict keys: {raw_dict.keys()}")
                        
                        # Navigate to function calls
                        if 'candidates' in raw_dict:
                            for candidate in raw_dict['candidates']:
                                if 'content' in candidate and 'parts' in candidate['content']:
                                    for part in candidate['content']['parts']:
                                        if 'function_call' in part:
                                            fc_dict = part['function_call']
                                            logger.info(f"🔍 Found function_call dict: {fc_dict}")
                                            
                                            if 'name' in fc_dict and fc_dict['name']:
                                                function_calls.append(fc_dict)
                                                logger.info(f"✅ Extracted: {fc_dict['name']}")
                except Exception as e:
                    logger.error(f"❌ Error serializing raw: {e}")
            
            # Alternative: Try to serialize response candidates directly
            if not function_calls and response.candidates:
                candidate = response.candidates[0]
                
                # Try to_dict on candidate
                try:
                    if hasattr(candidate, 'to_dict'):
                        cand_dict = candidate.to_dict()
                        logger.info(f"🔍 Candidate dict: {json.dumps(cand_dict, indent=2)[:500]}")
                        
                        if 'content' in cand_dict and 'parts' in cand_dict['content']:
                            for part in cand_dict['content']['parts']:
                                if 'function_call' in part:
                                    fc_dict = part['function_call']
                                    if 'name' in fc_dict and fc_dict['name']:
                                        function_calls.append(fc_dict)
                                        logger.info(f"✅ Extracted from candidate: {fc_dict['name']}")
                except Exception as e:
                    logger.error(f"❌ Error with candidate to_dict: {e}")
        
        except Exception as e:
            logger.error(f"❌ Raw extraction error: {e}", exc_info=True)
        
        return function_calls
    
    def _execute_function(self, function_call_dict) -> dict:
        """Execute function call from dict"""
        function_name = function_call_dict.get('name')
        function_args = function_call_dict.get('args', {})
        
        logger.info(f"🔧 Executing: {function_name}")
        logger.info(f"   Args: {json.dumps(function_args, indent=2)}")
        
        try:
            from agent.tools import calendar_tools
            
            if function_name == "add_calendar_event":
                result = calendar_tools.add_calendar_event(**function_args)
            elif function_name == "list_calendar_events":
                result = calendar_tools.list_calendar_events(**function_args)
            elif function_name == "delete_calendar_event":
                result = calendar_tools.delete_calendar_event(**function_args)
            elif function_name == "update_calendar_event":
                result = calendar_tools.update_calendar_event(**function_args)
            else:
                result = {
                    'success': False,
                    'error': f"Unknown function: {function_name}"
                }
            
            logger.info(f"✅ Executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process(self, user_id: str, message: str) -> str:
        """Main processing with function calling"""
        try:
            # Get or create chat session
            if user_id not in self.chat_sessions:
                self.chat_sessions[user_id] = self.model.start_chat(history=[])
            
            chat = self.chat_sessions[user_id]
            
            # Send message
            logger.info(f"📨 User: {message[:100]}...")
            response = chat.send_message(message)
            
            # Try to extract function calls from raw response
            function_calls = self._extract_function_calls_from_raw(response)
            
            logger.info(f"🔍 Extracted {len(function_calls)} function call(s)")
            
            # If no function calls, return text
            if not function_calls:
                logger.info("💬 No function calls, returning text")
                return response.text
            
            # Execute function calls
            logger.info(f"🔧 Executing {len(function_calls)} function(s)...")
            
            response_parts = []
            for fc_dict in function_calls:
                result = self._execute_function(fc_dict)
                
                # Build function response part
                response_parts.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fc_dict['name'],
                            response={'result': result}
                        )
                    )
                )
            
            # Get final response
            logger.info("🤖 Getting final response...")
            final_response = chat.send_message(response_parts)
            
            logger.info("✅ Process completed")
            return final_response.text
            
        except Exception as e:
            logger.error(f"❌ Process error: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"
    
    def chat(self, user_id: str, message: str) -> str:
        """Simple chat (delegates to process)"""
        return self.process(user_id, message)
    
    def clear_history(self, user_id: str) -> str:
        """Clear chat history"""
        if user_id in self.chat_sessions:
            del self.chat_sessions[user_id]
            return "✅ Chat history cleared!"
        return "ℹ️ No chat history to clear."
    
    def get_help(self) -> str:
        """Get help message"""
        base_help = """
🤖 **Bot Help:**

**Natural Chat:**
Just talk naturally! Examples:
- "jadwalin meeting besok jam 2"
- "apa jadwalku hari ini?"
- "tambahkan reminder olahraga jumat pagi"
"""
        
        if self.enable_calendar:
            base_help += """
**Calendar Keywords:**
- jadwal, schedule, meeting, event
- tambahkan, buatkan, jadwalin
- apa jadwalku, lihat agenda

**Commands:**
- `!list_events` - List events
- `!clear` - Clear chat
- `!help` - This message
"""
        
        return base_help
    
    def get_stats(self) -> str:
        """Get stats"""
        active_users = len(self.chat_sessions)
        calendar_status = "✅ Enabled" if self.enable_calendar else "❌ Disabled"
        
        return f"""
📊 **Bot Statistics:**
- Active users: {active_users}
- Model: {self.model_name}
- Calendar: {calendar_status}
- Status: ✅ Online
        """