from telethon import events
import aiohttp
import json
from bot.config.bot_config import Config
from app.core.backend_config import Settings
from bot.utils.logger import setup_logger

logger = setup_logger()
config = Config()

@events.register(events.NewMessage(pattern='/new_account'))
async def new_account(event: events.NewMessage.Event):
    """Create a new EVM-compatible account"""
    try:
        # Prepare the request payload
        payload = {
            "user_id": event.sender_id,
            "chain_id": Settings.CHAIN_ID,
            "import_private_key": None  # Generate new account
        }
        
        # Make API call to create account
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.API_BASE_URL}/account/create",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    account = data["account"]
                    mnemonic = data.get("mnemonic")
                    
                    # Format response message
                    response_text = f"""🎉 **New Account Created Successfully!**

📍 **Address:** `{account['address']}`
💰 **Balance:** {account['balance']} ETH
🔢 **Nonce:** {account['nonce']}
🌐 **Chain ID:** {account['chain_id']}

🔐 **Mnemonic Phrase:**
`{mnemonic}`

⚠️ **IMPORTANT:** Save your mnemonic phrase securely! This is the only way to recover your account."""
                    
                    await event.respond(response_text)
                    logger.info(f"New account {account['address']} created by user {event.sender_id}")
                    
                else:
                    error_data = await response.json()
                    error_msg = error_data.get("detail", "Unknown error occurred")
                    response_text = f"❌ **Error creating account:** {error_msg}"
                    await event.respond(response_text)
                    logger.error(f"Account creation failed for user {event.sender_id}: {error_msg}")
                    
    except aiohttp.ClientError as e:
        response_text = f"❌ **Network error:** Unable to connect to account service"
        await event.respond(response_text)
        logger.error(f"Network error creating account for user {event.sender_id}: {e}")
        
    except json.JSONDecodeError as e:
        response_text = f"❌ **Error:** Invalid response from account service"
        await event.respond(response_text)
        logger.error(f"JSON decode error for user {event.sender_id}: {e}")
        
    except Exception as e:
        response_text = f"❌ **Unexpected error:** {str(e)}"
        await event.respond(response_text)
        logger.error(f"Unexpected error creating account for user {event.sender_id}: {e}")

@events.register(events.NewMessage(pattern='/withdraw_funds'))
async def withdraw_funds(event: events.NewMessage.Event):
    """Handle /start command"""
    await event.respond('Welcome to AutoSomnia bot.')
    logger.info(f"Start command from user {event.sender_id}")

@events.register(events.NewMessage(pattern='/account_info'))
async def account_info(event: events.NewMessage.Event):
    """Handle /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
    """
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")