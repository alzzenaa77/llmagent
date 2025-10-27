import os
import google.generativeai as genai
from datetime import datetime

class LLMAgent:
    """LLM Agent using Google Gemini"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize LLM Agent
        
        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: gemini-2.5-flash)
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
            return f"❌ Error: {str(e)}"
    
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

**Basic:**
• `/chat <message>` - Chat dengan AI
• `/clear` - Hapus riwayat chat kamu
• `/help` - Lihat pesan ini

**Examples:**
• `/chat Halo! Siapa kamu?`
• `/chat Jelaskan tentang AI`
• `/chat Buatkan cerita pendek tentang robot`

**Features:**
✅ Conversational AI dengan memory
✅ Jawaban dalam Bahasa Indonesia
✅ Multi-user support
        """
    
    def get_stats(self) -> str:
        """Get bot statistics"""
        active_users = len(self.chat_sessions)
        return f"""
📊 **Bot Statistics:**
• Active users: {active_users}
• Model: {self.model_name}
• Status: ✅ Online
        """