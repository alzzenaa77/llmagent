import discord
from discord.ext import commands
from agent.llm_agent import LLMAgent
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordBot:
    """Discord Bot with LLM Agent integration"""
    
    def __init__(self, token: str, agent: LLMAgent, calendar_agent=None, prefix: str = "!"):
        """
        Initialize Discord Bot
        
        Args:
            token: Discord bot token
            agent: LLM Agent instance
            calendar_agent: Calendar Agent instance (optional)
            prefix: Command prefix (default: !)
        """
        self.token = token
        self.agent = agent
        self.calendar_agent = calendar_agent
        
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
            status_text = "!help for commands"
            if self.calendar_agent:
                status_text = "!help | Calendar enabled 📅"
            
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=status_text
                )
            )
        
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("❌ Missing argument! Use `!help` for command usage.")
            elif isinstance(error, commands.CommandNotFound):
                pass  # Ignore command not found errors
            else:
                logger.error(f"Error: {error}")
                await ctx.send(f"❌ An error occurred: {str(error)}")
    
    def _register_commands(self):
        # ===== DEBUG COMMAND (TEMPORARY) =====
        
        @self.bot.command(name='debug_parse', help='[DEBUG] Test calendar parsing')
        async def debug_parse(ctx, *, command: str):
            """Debug: Test intent parsing without executing"""
            try:
                async with ctx.typing():
                    intent = self.agent.parse_calendar_intent(command)
                    
                    if intent:
                        # Format intent for display
                        intent_str = "```json\n" + json.dumps(intent, indent=2) + "\n```"
                        await ctx.send(f"✅ **Parsed Intent:**\n{intent_str}")
                    else:
                        await ctx.send("❌ Failed to parse intent. Check bot logs.")
                    
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")
        """Register bot commands"""
        
        # ===== CHAT COMMANDS =====
        
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
        
        # ===== CALENDAR COMMANDS =====
        
        if self.calendar_agent:
            
            @self.bot.command(name='cal', help='Natural language calendar command')
            async def calendar_natural(ctx, *, command: str):
                """Process natural language calendar command"""
                try:
                    async with ctx.typing():
                        # Parse intent
                        intent = self.agent.parse_calendar_intent(command)
                        
                        if not intent:
                            await ctx.send(
                                "❌ Tidak bisa memahami perintah calendar.\n\n"
                                "**Contoh perintah:**\n"
                                "• `!cal buatkan meeting besok jam 2 siang`\n"
                                "• `!cal jadwalkan interview jumat pukul 10 pagi selama 2 jam`\n"
                                "• `!cal tampilkan jadwal hari ini`\n"
                                "• `!cal apa jadwalku minggu ini`\n"
                                "• `!cal hapus event abc123`\n"
                                "• `!cal update event abc123 judulnya jadi meeting penting`"
                            )
                            return
                        
                        # Execute action
                        action = intent.get('action')
                        
                        if action == 'create':
                            result = self.calendar_agent.create_event(
                                title=intent.get('title', 'Untitled Event'),
                                date=intent['date'],
                                time=intent['time'],
                                duration=intent.get('duration', 60),
                                description=intent.get('description', '')
                            )
                        
                        elif action == 'read':
                            result = self.calendar_agent.read_events(
                                date=intent.get('date'),
                                days=intent.get('days', 7)
                            )
                        
                        elif action == 'update':
                            update_data = {k: v for k, v in intent.items() 
                                          if k not in ['action', 'event_id'] and v}
                            result = self.calendar_agent.update_event(
                                event_id=intent['event_id'],
                                **update_data
                            )
                        
                        elif action == 'delete':
                            result = self.calendar_agent.delete_event(
                                event_id=intent['event_id']
                            )
                        
                        else:
                            result = {'success': False, 'message': '❌ Unknown action'}
                        
                        # Send response
                        await ctx.send(result['message'])
                        logger.info(f"Calendar action '{action}' by {ctx.author.name}: {command[:50]}")
                        
                except Exception as e:
                    logger.error(f"Calendar command error: {e}")
                    await ctx.send(f"❌ Error: {str(e)}")
            
            @self.bot.command(name='create_event', help='Create calendar event manually')
            async def create_event(ctx, title: str, date: str, time: str, duration: int = 60):
                """
                Create event with manual parameters
                
                Usage: !create_event "Meeting" 2025-10-29 14:00 60
                """
                try:
                    async with ctx.typing():
                        result = self.calendar_agent.create_event(
                            title=title,
                            date=date,
                            time=time,
                            duration=duration
                        )
                        await ctx.send(result['message'])
                        logger.info(f"Manual create event by {ctx.author.name}: {title}")
                except Exception as e:
                    await ctx.send(f"❌ Error: {str(e)}\n\n**Usage:** `!create_event \"Title\" YYYY-MM-DD HH:MM duration`")
            
            @self.bot.command(name='list_events', help='List calendar events')
            async def list_events(ctx, days: int = 7):
                """
                List events for specified days
                
                Usage: !list_events 7
                """
                try:
                    async with ctx.typing():
                        result = self.calendar_agent.read_events(days=days)
                        await ctx.send(result['message'])
                        logger.info(f"List events by {ctx.author.name}: {days} days")
                except Exception as e:
                    await ctx.send(f"❌ Error: {str(e)}")
            
            @self.bot.command(name='delete_event', help='Delete calendar event')
            async def delete_event(ctx, event_id: str):
                """
                Delete event by ID
                
                Usage: !delete_event abc123xyz
                """
                try:
                    async with ctx.typing():
                        result = self.calendar_agent.delete_event(event_id=event_id)
                        await ctx.send(result['message'])
                        logger.info(f"Delete event by {ctx.author.name}: {event_id}")
                except Exception as e:
                    await ctx.send(f"❌ Error: {str(e)}")
            
            @self.bot.command(name='update_event', help='Update calendar event')
            async def update_event_manual(ctx, event_id: str, field: str, *, value: str):
                """
                Update event field
                
                Usage: !update_event abc123 title New Title
                """
                try:
                    async with ctx.typing():
                        update_data = {field: value}
                        result = self.calendar_agent.update_event(
                            event_id=event_id,
                            **update_data
                        )
                        await ctx.send(result['message'])
                        logger.info(f"Update event by {ctx.author.name}: {event_id}")
                except Exception as e:
                    await ctx.send(f"❌ Error: {str(e)}")
        
        # ===== UTILITY COMMANDS =====
        
        @self.bot.command(name='help', help='Show help message')
        async def help_command(ctx):
            """Show help message"""
            help_text = self.agent.get_help()
            
            embed = discord.Embed(
                title="🤖 Bot Help & Commands",
                description=help_text,
                color=discord.Color.blue()
            )
            
            if self.calendar_agent:
                embed.set_footer(text="Made with ❤️ using Gemini AI & Google Calendar")
            else:
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