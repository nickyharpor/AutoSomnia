from telethon import events
from bot.utils.logger import setup_logger

logger = setup_logger()

@events.register(events.NewMessage(pattern='/suggest_exchange'))
async def suggest_exchange(event: events.NewMessage.Event):
    """Handle /start command"""
    await event.respond('Welcome to AutoSomnia bot.')
    logger.info(f"Start command from user {event.sender_id}")

@events.register(events.NewMessage(pattern='/auto_exchange_on'))
async def auto_exchange_on(event: events.NewMessage.Event):
    """Handle /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
    """
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")

@events.register(events.NewMessage(pattern='/auto_exchange_off'))
async def auto_exchange_off(event: events.NewMessage.Event):
    """Handle /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
    """
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")
