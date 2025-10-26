from telethon import events
from bot.utils.logger import setup_logger

logger = setup_logger()

@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event: events.NewMessage.Event):
    """Handle /start command"""
    await event.respond('Welcome to AutoSomnia bot.')
    logger.info(f"Start command from user {event.sender_id}")

@events.register(events.NewMessage(pattern='/help'))
async def help_handler(event: events.NewMessage.Event):
    """Handle /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
    """
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")

@events.register(events.NewMessage)
async def echo_handler(event: events.NewMessage.Event):
    """Echo non-command messages"""
    if not event.message.text.startswith('/'):
        await event.respond(f"You said: {event.message.text}")
        logger.info(f"Echo message from user {event.sender_id}")