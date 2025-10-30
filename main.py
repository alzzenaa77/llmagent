import os
from dotenv import load_dotenv
from agent.llm_agent import LLMAgent
from agent.tools import calendar_tools
from bot.discord_bot import DiscordBot
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from .env
    discord_token = os.getenv("DISCORD_TOKEN")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    bot_prefix = os.getenv("BOT_PREFIX", "!")
    llm_model = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
    
    # Calendar credentials
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials/credentials.json")
    token_path = os.getenv("GOOGLE_TOKEN_PATH", "credentials/token.json")
    
    # Validate credentials
    if not discord_token:
        print("❌ DISCORD_TOKEN not found in .env!")
        print("💡 Get your token from: https://discord.com/developers/applications")
        return
    
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in .env!")
        print("💡 Get your key from: https://aistudio.google.com/app/apikey")
        return
    
    print("="*60)
    print("🤖 Starting LLM Discord Bot with Calendar Integration")
    print("="*60)
    print(f"📝 Bot Prefix: {bot_prefix}")
    print(f"🧠 LLM Model: {llm_model}")
    print("="*60)
    
    try:
        # Initialize Calendar Tools first (if credentials exist)
        enable_calendar = False
        if os.path.exists(credentials_path):
            print("\n📅 Initializing Calendar Tools...")
            try:
                calendar_tools.init_calendar_agent(
                    credentials_path=credentials_path,
                    token_path=token_path
                )
                enable_calendar = True
                print("✅ Calendar Tools initialized!")
                print("   Calendar features: ENABLED (Function Calling)")
            except FileNotFoundError as e:
                print(f"⚠️  Calendar setup incomplete: {e}")
                print("   Calendar features: DISABLED")
            except Exception as e:
                print(f"⚠️  Calendar initialization error: {e}")
                print("   Calendar features: DISABLED")
        else:
            print("\n⚠️  Google Calendar credentials not found")
            print(f"   Expected path: {credentials_path}")
            print("   Calendar features: DISABLED")
            print("\n💡 To enable calendar features:")
            print("   1. Go to: https://console.cloud.google.com/")
            print("   2. Enable Google Calendar API")
            print("   3. Create OAuth 2.0 credentials (Desktop app)")
            print("   4. Download credentials.json")
            print("   5. Place in: credentials/credentials.json")
        
        # Initialize LLM Agent with calendar integration
        print("\n🧠 Initializing LLM Agent with Function Calling...")
        agent = LLMAgent(
            api_key=gemini_api_key,
            model_name=llm_model,
            enable_calendar=enable_calendar
        )
        print("✅ LLM Agent initialized with Function Calling!")
        
        # Initialize Discord Bot
        print("\n🤖 Initializing Discord Bot...")
        bot = DiscordBot(
            token=discord_token,
            agent=agent,
            calendar_agent=None,  # Not needed, integrated in LLMAgent
            prefix=bot_prefix
        )
        print("✅ Discord Bot initialized!")
        
        # Show available commands
        print("\n📋 Available Commands:")
        print("   • !chat <message> - Chat with AI")
        print("   • !help - Show all commands")
        print("   • !stats - Bot statistics")
        print("   • !ping - Check latency")
        print("   • !clear - Clear chat history")
        
        if enable_calendar:
            print("\n📅 Calendar Commands (Natural Language):")
            print("   Just chat naturally without prefix! Examples:")
            print("   • 'Tambahkan jadwal rapat besok jam 10 pagi'")
            print("   • 'Apa jadwalku hari ini?'")
            print("   • 'Lihat agenda minggu ini'")
            print("   • 'Hapus event [event_id]'")
            print("\n   Or use explicit commands:")
            print("   • !list_events - List upcoming events")
        
        # Run bot
        print("\n🚀 Starting bot...\n")
        print("="*60)
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if DISCORD_TOKEN is valid")
        print("   2. Check if GEMINI_API_KEY is valid")
        print("   3. Check internet connection")
        print("   4. Ensure MESSAGE CONTENT INTENT is enabled in Discord Developer Portal")
        print("   5. For calendar: ensure credentials.json exists")
        print("   6. Check logs above for detailed error")

if __name__ == "__main__":
    main()