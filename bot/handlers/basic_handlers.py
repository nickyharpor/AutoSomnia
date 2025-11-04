from telethon import events
from utils.logger import setup_logger
from config.bot_config import Config
import sys
import os
import aiohttp
import json

# Add the parent directory to the path to import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

config = Config()
logger = setup_logger(config.LOG_LEVEL)

@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event: events.NewMessage.Event):
    """Handle /start command and register new users"""
    try:
        user_id = event.sender_id
        
        # Check if user exists in database and create if not
        async with aiohttp.ClientSession() as session:
            # Check if user exists by making a request to get user data
            try:
                async with session.get(
                    f"{config.API_BASE_URL}/users/{user_id}"
                ) as response:
                    
                    if response.status == 404:
                        # 404 => User doesn't exist, create new user
                        user_data = {
                            "user_id": user_id,
                            "auto_exchange": False
                        }
                        
                        async with session.post(
                            f"{config.API_BASE_URL}/users/create",
                            json=user_data,
                            headers={"Content-Type": "application/json"}
                        ) as create_response:
                            
                            if create_response.status == 200:
                                logger.info(f"New user created: {user_id}")
                                welcome_message = """🌙 **Welcome to AutoSomnia!**

**Close your eyes and let AutoSomnia trade for you.**

🤖 **What I can do for you:**
• Create and manage Web3 wallets
• Get AI-powered trading suggestions
• Buy/sell USD tokens automatically
• Send funds with simple commands
• Monitor your portfolio

📋 **Quick Start:**
• `/new_account` - Create your first wallet
• `/account_info` - Check your balances
• `/suggest_exchange` - Get trading advice
• `/help` - See all commands

💡 **Pro tip:** Fund your account and try `/buy_usd 0.1` to get started with trading!

Sweet dreams, profitable trades! 🌙"""
                            else:
                                logger.error(f"Failed to create user {user_id}")
                                welcome_message = "🌙 **Welcome to AutoSomnia!** There was an issue setting up your account, but you can still use the bot."
                    
                    elif response.status == 200:
                        # User exists, show returning user message
                        user_data = await response.json()
                        auto_exchange_status = "ON" if user_data.get("auto_exchange", False) else "OFF"
                        
                        logger.info(f"Returning user: {user_id}")
                        welcome_message = f"""🌙 **Welcome back to AutoSomnia!**

**Your account status:**
• Auto-exchange: {auto_exchange_status}
• Ready to trade: ✅

📋 **Quick Actions:**
• `/account_info` - Check your balances
• `/suggest_exchange` - Get fresh trading advice
• `/buy_usd <amount>` - Buy USD tokens
• `/auto_exchange_on` - Enable automated trading
• `/withdraw_funds <address>` - Withdraw all SOMI to <address>

💡 **Need help?** Use `/help` to see all available commands.

Sweet dreams, profitable trades! 🌙"""
                    
                    else:
                        # Unexpected response, show generic welcome
                        logger.warning(f"Unexpected response checking user {user_id}: {response.status}")
                        welcome_message = "🌙 **Welcome to AutoSomnia!** Your personal AI trading assistant."
                        
            except aiohttp.ClientError as e:
                logger.error(f"Network error checking user {user_id}: {e}")
                welcome_message = "🌙 **Welcome to AutoSomnia!** Your personal AI trading assistant."
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON error for user {user_id}: {e}")
                welcome_message = "🌙 **Welcome to AutoSomnia!** Your personal AI trading assistant."
        
        await event.respond(welcome_message)
        logger.info(f"Start command processed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Unexpected error in start_handler for user {event.sender_id}: {e}")
        await event.respond("🌙 **Welcome to AutoSomnia!** Your personal AI trading assistant.")

@events.register(events.NewMessage(pattern='/help'))
async def help_handler(event: events.NewMessage.Event):
    """Handle /help command"""
    help_text = """🌙 **AutoSomnia Bot Commands**

**💼 Account Management:**
• `/new_account` - Create a new Web3 wallet
• `/account_info` - View your account details and balances
• `/withdraw_funds <address>` - Send all SOMI to address
• `/withdraw_funds <address> <token>` - Send all tokens to address

**💱 Trading Commands:**
• `/suggest_exchange` - Get AI-powered trading advice
• `/buy_usd <amount>` - Buy USD tokens with SOMI
• `/sell_usd <amount>` - Sell USD tokens for SOMI
• `/auto_exchange_on` - Enable automated trading
• `/auto_exchange_off` - Disable automated trading

**ℹ️ General:**
• `/start` - Welcome message and setup
• `/help` - Show this help message

**💡 Examples:**
• `/new_account` - Creates your first wallet
• `/buy_usd 0.1` - Buys 0.1 SOMI worth of USDT tokens
• `/suggest_exchange` - Gets AI trading recommendation

**⚠️ Need help?** Each command shows detailed help when used without parameters.

Sweet dreams, profitable trades! 🌙"""
    
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")

@events.register(events.NewMessage)
async def echo_handler(event: events.NewMessage.Event):
    """Echo non-command messages"""
    if not event.message.text.startswith('/'):
        await event.respond(f"You said: {event.message.text}")
        logger.info(f"Echo message from user {event.sender_id}")