import discord
from discord.ext import commands
from agent.llm_agent import LLMAgent
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordBot:
    """Discord Bot with LLM Agent integration"""
    
    def __init__(self, token: str, agent: LLMAgent, prefix: str = "!"):
        """
        Initialize Discord Bot
        
        Args:
            token: Discord bot token
            agent: LLM Agent instance
            prefix: Command prefix (default: !)
        """
        self.token = token
        self.agent = agent
        
        # Setup bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        self.bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)
        
        # Register events and commands
        self._register_events()
        self._register_commands()
    
    def _register_events(self):
        """Register bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'✅ Bot is ready! Logged in as {self.bot.user}')
            logger.info(f'Bot is in {len(self.bot.guilds)} servers')
            
            # Set bot status
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name="/help untuk bantuan"
                )
            )
        
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("❌ Missing argument! Use `/help` for command usage.")
            else:
                logger.error(f"Error: {error}")
                await ctx.send(f"❌ An error occurred: {str(error)}")
    
    def _register_commands(self):
        """Register bot commands"""
        
        @self.bot.command(name='chat', help='Chat with AI')
        async def chat(ctx, *, message: str):
            """Chat with the AI"""
            try:
                # Show typing indicator
                async with ctx.typing():
                    # Get user ID
                    user_id = str(ctx.author.id)
                    
                    # Get AI response
                    response = self.agent.chat(user_id, message)
                    
                    # Send response (split if too long)
                    if len(response) > 2000:
                        # Split into chunks
                        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                        for chunk in chunks:
                            await ctx.send(chunk)
                    else:
                        await ctx.send(response)
                    
                    logger.info(f"User {ctx.author.name} chatted: {message[:50]}...")
                    
            except Exception as e:
                logger.error(f"Chat error: {e}")
                await ctx.send(f"❌ Error: {str(e)}")
        
        @self.bot.command(name='clear', help='Clear your chat history')
        async def clear(ctx):
            """Clear user's chat history"""
            user_id = str(ctx.author.id)
            result = self.agent.clear_history(user_id)
            await ctx.send(result)
            logger.info(f"User {ctx.author.name} cleared history")
        
        @self.bot.command(name='help', help='Show help message')
        async def help_command(ctx):
            """Show help message"""
            help_text = self.agent.get_help()
            
            embed = discord.Embed(
                title="🤖 Bot Help",
                description=help_text,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Made with ❤️ using Gemini AI")
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='stats', help='Show bot statistics')
        async def stats(ctx):
            """Show bot statistics"""
            stats_text = self.agent.get_stats()
            
            embed = discord.Embed(
                title="📊 Bot Statistics",
                description=stats_text,
                color=discord.Color.green()
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='ping', help='Check bot latency')
        async def ping(ctx):
            """Check bot latency"""
            latency = round(self.bot.latency * 1000)
            await ctx.send(f"🏓 Pong! Latency: {latency}ms")
    
    def run(self):
        """Start the bot"""
        logger.info("🚀 Starting Discord bot...")
        self.bot.run(self.token)