import os
from dotenv import load_dotenv
from agent.llm_agent import LLMAgent
from bot.discord_bot import DiscordBot

def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials from .env
    discord_token = os.getenv("DISCORD_TOKEN")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    bot_prefix = os.getenv("BOT_PREFIX", "!")
    llm_model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
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
    print("🤖 Starting LLM Discord Bot")
    print("="*60)
    print(f"📝 Bot Prefix: {bot_prefix}")
    print(f"🧠 LLM Model: {llm_model}")
    print("="*60)
    
    try:
        # Initialize LLM Agent
        print("\n🧠 Initializing LLM Agent...")
        agent = LLMAgent(api_key=gemini_api_key, model_name=llm_model)
        print("✅ LLM Agent initialized!")
        
        # Initialize Discord Bot
        print("\n🤖 Initializing Discord Bot...")
        bot = DiscordBot(token=discord_token, agent=agent, prefix=bot_prefix)
        print("✅ Discord Bot initialized!")
        
        # Run bot
        print("\n🚀 Starting bot...\n")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if DISCORD_TOKEN is valid")
        print("   2. Check if GEMINI_API_KEY is valid")
        print("   3. Check internet connection")
        print("   4. Make sure bot has MESSAGE CONTENT INTENT enabled")

if __name__ == "__main__":
    main()