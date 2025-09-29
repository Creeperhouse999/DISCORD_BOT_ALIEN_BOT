import discord
from discord.ext import commands
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from api.health import start_health_api

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AlienBot')

# Create a separate logger for console output without emojis
console_logger = logging.getLogger('AlienBot.Console')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_logger.addHandler(console_handler)
console_logger.setLevel(logging.INFO)

load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("INTERACT")
CHANNEL_ID = os.getenv("CHANNEL_ID")

intents = discord.Intents.default()
# Enable these privileged intents - REQUIRED for bot to work in channels
intents.message_content = True
intents.members = True

# Function to check for ! prefix
def get_prefix(bot, message):
    """Check for ! prefix"""
    return commands.when_mentioned_or("!")(bot, message)

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

def should_respond_in_channel(channel):
    """Check if bot should respond in this channel"""
    if not CHANNEL_ID or CHANNEL_ID.strip() == "":
        return True  # No channel restriction, respond everywhere
    
    try:
        target_channel_id = int(CHANNEL_ID)
        return channel.id == target_channel_id
    except (ValueError, TypeError):
        logger.warning(f"Invalid CHANNEL_ID format: {CHANNEL_ID}")
        return True  # If invalid, respond everywhere

async def load_cogs():
    """Load all cogs from the cogs directory"""
    logger.info("🤖 Starting to load cogs...")
    console_logger.info("Starting to load cogs...")
    cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
    
    if not os.path.exists(cogs_path):
        logger.error(f"❌ Cogs directory not found: {cogs_path}")
        console_logger.error(f"Cogs directory not found: {cogs_path}")
        return
    
    loaded_cogs = []
    failed_cogs = []
    
    for filename in os.listdir(cogs_path):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                loaded_cogs.append(filename[:-3])
                logger.info(f"✅ Successfully loaded cog: {filename[:-3]}")
                console_logger.info(f"Successfully loaded cog: {filename[:-3]}")
            except Exception as e:
                failed_cogs.append((filename[:-3], str(e)))
                logger.error(f"❌ Failed to load cog {filename[:-3]}: {e}")
                console_logger.error(f"Failed to load cog {filename[:-3]}: {e}")
    
    logger.info(f"🎯 Cog loading complete. Loaded: {len(loaded_cogs)}, Failed: {len(failed_cogs)}")
    console_logger.info(f"Cog loading complete. Loaded: {len(loaded_cogs)}, Failed: {len(failed_cogs)}")
    if loaded_cogs:
        logger.info(f"📦 Loaded cogs: {', '.join(loaded_cogs)}")
        console_logger.info(f"Loaded cogs: {', '.join(loaded_cogs)}")
    if failed_cogs:
        logger.error(f"💥 Failed cogs: {', '.join([f'{name}({error})' for name, error in failed_cogs])}")
        console_logger.error(f"Failed cogs: {', '.join([f'{name}({error})' for name, error in failed_cogs])}")

@bot.event
async def on_ready():
    logger.info("=" * 50)
    logger.info("🤖 ALIEN BOT STARTING UP 🤖")
    logger.info("=" * 50)
    console_logger.info("=" * 50)
    console_logger.info("ALIEN BOT STARTING UP")
    console_logger.info("=" * 50)
    
    try:
        await load_cogs()
        await bot.tree.sync()
        
        logger.info(f"✅ Bot is ready! Logged in as {bot.user}")
        logger.info(f"📊 Bot ID: {bot.user.id}")
        logger.info(f"🏠 Connected to {len(bot.guilds)} guild(s)")
        
        console_logger.info(f"Bot is ready! Logged in as {bot.user}")
        console_logger.info(f"Bot ID: {bot.user.id}")
        console_logger.info(f"Connected to {len(bot.guilds)} guild(s)")
        
        # Log prefix and channel configuration
        logger.info(f"🔧 Bot prefix: ! (or @AlienBot mention)")
        console_logger.info(f"Bot prefix: ! (or @AlienBot mention)")
        
        if CHANNEL_ID and CHANNEL_ID.strip():
            try:
                target_channel_id = int(CHANNEL_ID)
                logger.info(f"🎯 Bot configured to respond only in channel ID: {target_channel_id}")
                console_logger.info(f"Bot configured to respond only in channel ID: {target_channel_id}")
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Invalid CHANNEL_ID format: {CHANNEL_ID}")
                console_logger.warning(f"Invalid CHANNEL_ID format: {CHANNEL_ID}")
        else:
            logger.info("🌐 Bot configured to respond in all channels")
            console_logger.info("Bot configured to respond in all channels")
        
        if bot.guilds:
            guild_names = [guild.name for guild in bot.guilds]
            logger.info(f"🏰 Guild names: {', '.join(guild_names)}")
            console_logger.info(f"Guild names: {', '.join(guild_names)}")
        
        # Start health API
        start_health_api()
        
        logger.info("🚀 Bot is now online and ready to receive commands!")
        logger.info("=" * 50)
        console_logger.info("Bot is now online and ready to receive commands!")
        console_logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error during bot startup: {e}")
        console_logger.error(f"Error during bot startup: {e}")

@bot.event
async def on_command(ctx):
    """Log when a command is used"""
    logger.info(f"📝 Command used: {ctx.command.name} by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")

@bot.event
async def on_command_error(ctx, error):
    """Log command errors"""
    logger.error(f"❌ Command error: {ctx.command.name} by {ctx.author} - {error}")

@bot.event
async def on_message(message):
    """Log all messages and check channel restrictions"""
    if message.author != bot.user:  # Don't log bot's own messages
        logger.debug(f"💬 Message: {message.author} in {message.guild.name if message.guild else 'DM'}: {message.content[:100]}...")
    
    # Debug logging for channel filtering
    if message.guild:
        logger.debug(f"🔍 Processing message in guild: {message.guild.name}, channel: {message.channel.name} (ID: {message.channel.id})")
        
        # Check if bot should respond in this channel
        if not should_respond_in_channel(message.channel):
            logger.debug(f"🚫 Ignoring message in channel {message.channel.name} (ID: {message.channel.id}) - not the target channel")
            return
        else:
            logger.debug(f"✅ Channel {message.channel.name} is allowed - processing command")
    else:
        logger.debug(f"📱 Processing DM from {message.author}")
    
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    """Log when bot joins a new guild"""
    logger.info(f"🎉 Joined new guild: {guild.name} (ID: {guild.id}) with {guild.member_count} members")

@bot.event
async def on_guild_remove(guild):
    """Log when bot leaves a guild"""
    logger.info(f"👋 Left guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_disconnect():
    """Log when bot disconnects"""
    logger.warning("⚠️ Bot disconnected from Discord")

@bot.event
async def on_resumed():
    """Log when bot reconnects"""
    logger.info("🔄 Bot reconnected to Discord")

if __name__ == "__main__":
    logger.info("🚀 Starting AlienBot...")
    console_logger.info("Starting AlienBot...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        console_logger.error(f"Fatal error: {e}")
    finally:
        logger.info("🛑 Bot shutdown complete")
        console_logger.info("Bot shutdown complete")