import os
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import logging
import re

logger = logging.getLogger(__name__)

class LLMAgent:
    """LLM Agent using Google Gemini"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize LLM Agent
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(model_name=self.model_name)

        # System instruction will be added in first message
        self.system_prompt = """Kamu adalah asisten AI yang membantu dan ramah. 
        Kamu bisa:
        - Menjawab pertanyaan umum
        - Memberikan penjelasan tentang berbagai topik
        - Membantu brainstorming ide
        - Memberikan saran dan tips

        Selalu jawab dengan bahasa Indonesia yang santai dan mudah dipahami."""
        
        # Chat history storage
        self.chat_sessions = {}
        
    def chat(self, user_id: str, message: str) -> str:
        """
        Send message to LLM and get response
        
        Args:
            user_id: Unique user identifier
            message: User message
            
        Returns:
            AI response
        """
        try:
            # Get or create chat session for user
            if user_id not in self.chat_sessions:
                # Start new chat with system prompt as first message
                self.chat_sessions[user_id] = self.model.start_chat(
                    history=[
                        {"role": "user", "parts": [self.system_prompt]},
                        {"role": "model", "parts": ["Baik, saya siap membantu!"]}
                    ]
                )
            
            chat = self.chat_sessions[user_id]
            
            # Send message and get response
            response = chat.send_message(message)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"❌ Error: {str(e)}"
    
    def parse_calendar_intent(self, message: str) -> dict:
        """
        Parse calendar intent from natural language
        
        Args:
            message: User message
            
        Returns:
            Dictionary with parsed intent
        """
        try:
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            
            today_str = today.strftime("%Y-%m-%d")
            tomorrow_str = tomorrow.strftime("%Y-%m-%d")
            day_name = today.strftime("%A")
            current_time = datetime.now().strftime("%H:%M")
            
            # Create simpler, more direct prompt
            system_prompt = f"""You are a JSON parser for Google Calendar commands. You MUST respond with ONLY valid JSON, nothing else.

Current context:
- Today: {today_str} ({day_name})
- Tomorrow: {tomorrow_str}
- Current time: {current_time}

Parse the user command and extract:
- action: "create", "read", "update", or "delete"
- title: event title (for create/update)
- date: date in YYYY-MM-DD format
- time: time in HH:MM format (24-hour)
- duration: duration in minutes (default 60)
- description: event description (optional)
- event_id: event ID (for update/delete)
- days: number of days (for read, default 7)

Date parsing rules:
- "besok" = {tomorrow_str}
- "hari ini" = {today_str}
- "lusa" = {(today + timedelta(days=2)).strftime("%Y-%m-%d")}
- If no specific date for "read", omit the "date" field

Time parsing rules:
- "pagi" = 09:00
- "siang" = 12:00
- "sore" = 15:00
- "malam" = 19:00
- "jam 2" or "jam 14" = convert to HH:MM format
- "2 siang" = 14:00

User command: "{message}"

Respond with ONLY the JSON object, no markdown, no explanation:"""
            
            # Get response from Gemini
            response = self.model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            logger.info(f"Raw Gemini response: {response_text}")
            
            # Clean response - remove markdown, backticks, extra text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Try to extract JSON from response if it contains extra text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            logger.info(f"Cleaned response: {response_text}")
            
            # Parse JSON
            intent = json.loads(response_text)
            
            logger.info(f"Parsed intent: {intent}")
            
            # Validate action
            valid_actions = ['create', 'read', 'update', 'delete']
            if intent.get('action') not in valid_actions:
                logger.warning(f"Invalid action: {intent.get('action')}")
                return None
            
            # Validate required fields per action
            action = intent.get('action')
            
            if action == 'create':
                required = ['title', 'date', 'time']
                missing = [field for field in required if field not in intent or not intent[field]]
                if missing:
                    logger.warning(f"Missing required fields for create: {missing}")
                    return None
            
            elif action in ['update', 'delete']:
                if 'event_id' not in intent or not intent['event_id']:
                    logger.warning(f"Missing event_id for {action}")
                    return None
            
            # Set defaults
            if action == 'create' and 'duration' not in intent:
                intent['duration'] = 60
            
            if action == 'read' and 'date' not in intent and 'days' not in intent:
                intent['days'] = 7
            
            return intent
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error: {e}")
            logger.error(f"Response text was: {response_text}")
            
            # Fallback: Try manual parsing for common patterns
            return self._fallback_parse(message, today_str, tomorrow_str)
            
        except Exception as e:
            logger.error(f"Parse intent error: {e}", exc_info=True)
            return None
    
    def _fallback_parse(self, message: str, today_str: str, tomorrow_str: str) -> dict:
        """
        Fallback manual parsing when Gemini fails
        
        Args:
            message: User message
            today_str: Today's date string
            tomorrow_str: Tomorrow's date string
        """
        try:
            message_lower = message.lower()
            logger.info(f"Using fallback parser for: {message}")
            
            # Detect action
            if any(word in message_lower for word in ['buat', 'buatkan', 'jadwal', 'jadwalkan', 'tambah']):
                action = 'create'
            elif any(word in message_lower for word in ['tampil', 'tampilkan', 'lihat', 'cek', 'jadwal']):
                action = 'read'
            elif any(word in message_lower for word in ['hapus', 'delete']):
                action = 'delete'
            elif any(word in message_lower for word in ['update', 'ubah', 'ganti']):
                action = 'update'
            else:
                logger.warning("Could not detect action in fallback parse")
                return None
            
            intent = {'action': action}
            
            # Parse based on action
            if action == 'create':
                # Extract date
                if 'besok' in message_lower:
                    intent['date'] = tomorrow_str
                elif 'hari ini' in message_lower:
                    intent['date'] = today_str
                else:
                    # Default to tomorrow if no date specified
                    intent['date'] = tomorrow_str
                
                # Extract time
                if 'pagi' in message_lower:
                    intent['time'] = '09:00'
                elif 'siang' in message_lower:
                    intent['time'] = '12:00'
                elif 'sore' in message_lower:
                    intent['time'] = '15:00'
                elif 'malam' in message_lower:
                    intent['time'] = '19:00'
                else:
                    # Try to extract "jam X"
                    time_match = re.search(r'jam\s+(\d+)', message_lower)
                    if time_match:
                        hour = int(time_match.group(1))
                        if hour <= 12 and 'siang' not in message_lower:
                            hour += 12  # Assume PM if not specified
                        intent['time'] = f"{hour:02d}:00"
                    else:
                        intent['time'] = '14:00'  # Default 2 PM
                
                # Extract title (everything before date/time words)
                title_words = []
                skip_words = ['buat', 'buatkan', 'jadwal', 'jadwalkan', 'besok', 'hari', 'ini', 
                             'jam', 'pagi', 'siang', 'sore', 'malam', 'selama']
                for word in message.split():
                    if word.lower() not in skip_words and not word.isdigit():
                        title_words.append(word)
                    if word.lower() in ['besok', 'jam']:
                        break
                
                intent['title'] = ' '.join(title_words) if title_words else 'Event'
                intent['duration'] = 60
                
                logger.info(f"Fallback parsed CREATE: {intent}")
                return intent
            
            elif action == 'read':
                if 'hari ini' in message_lower:
                    intent['date'] = today_str
                elif 'besok' in message_lower:
                    intent['date'] = tomorrow_str
                else:
                    intent['days'] = 7
                
                logger.info(f"Fallback parsed READ: {intent}")
                return intent
            
            elif action == 'delete':
                # Try to extract event ID
                id_match = re.search(r'event\s+([a-zA-Z0-9_-]+)', message_lower)
                if id_match:
                    intent['event_id'] = id_match.group(1)
                    logger.info(f"Fallback parsed DELETE: {intent}")
                    return intent
                else:
                    logger.warning("Could not extract event_id in fallback")
                    return None
            
            elif action == 'update':
                # Try to extract event ID
                id_match = re.search(r'event\s+([a-zA-Z0-9_-]+)', message_lower)
                if id_match:
                    intent['event_id'] = id_match.group(1)
                    
                    # Extract new title if present
                    title_match = re.search(r'judul(?:nya)?\s+jadi\s+(.+)', message_lower)
                    if title_match:
                        intent['title'] = title_match.group(1).strip()
                    
                    logger.info(f"Fallback parsed UPDATE: {intent}")
                    return intent
                else:
                    logger.warning("Could not extract event_id in fallback")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback parse error: {e}", exc_info=True)
            return None
    
    def clear_history(self, user_id: str) -> str:
        """Clear chat history for a user"""
        if user_id in self.chat_sessions:
            del self.chat_sessions[user_id]
            return "✅ Chat history cleared!"
        return "ℹ️ No chat history to clear."
    
    def get_help(self) -> str:
        """Get help message"""
        return """
🤖 **Bot Commands:**

**Chat Commands:**
- `!chat <message>` - Chat dengan AI
- `!clear` - Hapus riwayat chat kamu

**Calendar Commands (Natural Language):**
- `!cal buatkan meeting besok jam 2 siang`
- `!cal jadwalkan interview jumat pukul 10 pagi selama 2 jam`
- `!cal tampilkan jadwal hari ini`
- `!cal apa jadwalku minggu ini`
- `!cal hapus event <event_id>`
- `!cal update event <event_id> judulnya jadi <judul baru>`

**Calendar Commands (Manual):**
- `!create_event "<title>" YYYY-MM-DD HH:MM <duration>`
- `!list_events <days>`
- `!delete_event <event_id>`

**Other Commands:**
- `!help` - Lihat pesan ini
- `!stats` - Statistik bot
- `!ping` - Cek latency bot

**Examples:**
- `!chat Jelaskan tentang AI`
- `!cal buatkan rapat besok pagi`
- `!create_event "Team Meeting" 2025-10-29 14:00 60`
- `!list_events 7`

**Features:**
✅ Conversational AI dengan memory
✅ Natural language calendar commands
✅ Google Calendar integration (CRUD)
✅ Multi-user support
        """
    
    def get_stats(self) -> str:
        """Get bot statistics"""
        active_users = len(self.chat_sessions)
        return f"""
📊 **Bot Statistics:**
- Active chat users: {active_users}
- LLM Model: {self.model_name}
- Calendar: ✅ Integrated
- Status: ✅ Online
        """