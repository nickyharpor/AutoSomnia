from telethon import events
import aiohttp
import json
from config.bot_config import Config # type: ignore
from utils.logger import setup_logger # type: ignore
from app.core.backend_config import settings

config = Config()
logger = setup_logger(config.LOG_LEVEL)

@events.register(events.NewMessage(pattern='/new_account'))
async def new_account(event: events.NewMessage.Event):
    """Create a new EVM-compatible account"""
    try:
        # Prepare the request payload
        payload = {
            "user_id": event.sender_id,
            "chain_id": settings.CHAIN_ID,  # Use chain ID from backend config
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


@events.register(events.NewMessage(pattern=r'/withdraw_funds\s+(\S+)(?:\s+(\S+))?'))
async def withdraw_funds_handler(event):
    """Handle withdraw funds command with format: /withdraw_funds <to_address> [token_address]"""
    try:
        # Extract addresses from the command
        to_address = event.pattern_match.group(1).strip()
        token_address = event.pattern_match.group(2)
        if token_address:
            token_address = token_address.strip()
        
        user_id = event.sender_id
        
        # Get user's account from database
        async with aiohttp.ClientSession() as session:
            # First, get user's accounts
            async with session.get(
                f"{config.API_BASE_URL}/account/list_user_accounts/{user_id}"
            ) as response:
                
                if response.status != 200:
                    await event.reply("❌ **Error:** Unable to retrieve your accounts")
                    return
                
                data = await response.json()
                accounts = data.get("accounts", [])
                
                if not accounts:
                    await event.reply("❌ **No accounts found.** Create an account first with /new_account")
                    return
                
                # Use the first account (you might want to implement account selection)
                account = accounts[0]
                private_key = account["private_key"]
                from_address = account["address"]
                
                if token_address:
                    # Send tokens
                    await event.reply(f"🔄 **Sending tokens to** `{to_address}`...")
                    
                    payload = {
                        "private_key": private_key,
                        "to_address": to_address,
                        "token_address": token_address,
                        "amount": "MAX"
                    }
                    
                    async with session.post(
                        f"{config.API_BASE_URL}/account/send-token",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as tx_response:
                        
                        if tx_response.status == 200:
                            tx_data = await tx_response.json()
                            
                            response_text = f"""✅ **Token Transfer Successful!**

📤 **From:** `{from_address}`
📥 **To:** `{to_address}`
💰 **Amount:** {tx_data['amount']} tokens
🔗 **Transaction Hash:** `{tx_data['transaction_hash']}`
⛽ **Gas Cost:** {tx_data['estimated_gas_cost']} SOMI

🔍 **Transaction is being processed on the blockchain...**"""
                            
                            await event.reply(response_text)
                            logger.info(f"Token transfer successful: {tx_data['transaction_hash']} by user {user_id}")
                            
                        else:
                            error_data = await tx_response.json()
                            error_msg = error_data.get("detail", "Unknown error occurred")
                            await event.reply(f"❌ **Token transfer failed:** {error_msg}")
                            logger.error(f"Token transfer failed for user {user_id}: {error_msg}")
                
                else:
                    # Send ETH
                    await event.reply(f"🔄 **Sending SOMI to** `{to_address}`...")
                    
                    payload = {
                        "private_key": private_key,
                        "to_address": to_address,
                        "amount": "MAX"
                    }
                    
                    async with session.post(
                        f"{config.API_BASE_URL}/account/send-eth",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as tx_response:
                        
                        if tx_response.status == 200:
                            tx_data = await tx_response.json()
                            
                            response_text = f"""✅ **SOMI Transfer Successful!**

📤 **From:** `{from_address}`
📥 **To:** `{to_address}`
💰 **Amount:** {tx_data['amount']} SOMI
🔗 **Transaction Hash:** `{tx_data['transaction_hash']}`
⛽ **Gas Cost:** {tx_data['estimated_gas_cost']} SOMI

🔍 **Transaction is being processed on the blockchain...**"""
                            
                            await event.reply(response_text)
                            logger.info(f"SOMI transfer successful: {tx_data['transaction_hash']} by user {user_id}")
                            
                        else:
                            error_data = await tx_response.json()
                            error_msg = error_data.get("detail", "Unknown error occurred")
                            await event.reply(f"❌ **SOMI transfer failed:** {error_msg}")
                            logger.error(f"SOMI transfer failed for user {user_id}: {error_msg}")
                            
    except aiohttp.ClientError as e:
        await event.reply("❌ **Network error:** Unable to connect to account service")
        logger.error(f"Network error in withdraw_funds for user {event.sender_id}: {e}")
        
    except json.JSONDecodeError as e:
        await event.reply("❌ **Error:** Invalid response from account service")
        logger.error(f"JSON decode error in withdraw_funds for user {event.sender_id}: {e}")
        
    except Exception as e:
        await event.reply(f"❌ **Unexpected error:** {str(e)}")
        logger.error(f"Unexpected error in withdraw_funds for user {event.sender_id}: {e}")


@events.register(events.NewMessage(pattern='/withdraw_funds'))
async def withdraw_funds_help(event):
    """Show help for withdraw_funds command when no parameters provided"""
    help_text = """💸 **Withdraw Funds Help**

**Usage:**
• `/withdraw_funds <to_address>` - Send all SOMI to address
• `/withdraw_funds <to_address> <token_address>` - Send all tokens to address

**Examples:**
• `/withdraw_funds 0x742d35Cc6634C0532925a3b8D4C9db96590c6C87`
• `/withdraw_funds 0x742d35Cc6634C0532925a3b8D4C9db96590c6C87 0xA0b86a33E6441e8e421c7c7c4b8c9b8c8c8c8c8c`

⚠️ **Note:** This will send the MAXIMUM available amount (minus gas fees for SOMI)"""
    
    await event.reply(help_text)
    logger.info(f"Withdraw funds help shown to user {event.sender_id}")

@events.register(events.NewMessage(pattern='/account_info'))
async def account_info(event: events.NewMessage.Event):
    """Show account information for the user"""
    try:
        user_id = event.sender_id
        
        # Get user's accounts from database
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.API_BASE_URL}/account/list_user_accounts/{user_id}"
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    accounts = data.get("accounts", [])
                    
                    if not accounts:
                        response_text = """📊 **Account Information**

❌ **No accounts found**

Create your first account with `/new_account`"""
                    else:
                        response_text = f"📊 **Account Information**\n\n**Total Accounts:** {len(accounts)}\n\n"
                        
                        for i, account in enumerate(accounts, 1):
                            address = account["address"]
                            is_imported = account.get("is_imported", False)
                            created_at = account.get("created_at", "Unknown")
                            
                            # Get balance for each account
                            async with session.get(
                                f"{config.API_BASE_URL}/account/balance/{address}"
                            ) as balance_response:
                                
                                if balance_response.status == 200:
                                    balance_data = await balance_response.json()
                                    balance = balance_data["balance_eth"]
                                else:
                                    balance = "Error fetching"
                            
                            account_type = "Imported" if is_imported else "Generated"
                            
                            response_text += f"""**Account {i}:**
📍 **Address:** `{address}`
💰 **Balance:** {balance} SOMI
🔧 **Type:** {account_type}
📅 **Created:** {created_at}

"""
                        
                        response_text += """**Available Commands:**
• `/new_account` - Create new account
• `/withdraw_funds <address>` - Send all SOMI
• `/withdraw_funds <address> <token>` - Send all tokens
• `/buy_usd <amount>` - Buy <amount> SOMI worth of USDT tokens 
• `/sell_usd <amount>` - Sell <amount> USDT tokens"""
                    
                    await event.respond(response_text)
                    logger.info(f"Account info shown to user {user_id}")
                    
                else:
                    await event.respond("❌ **Error:** Unable to retrieve account information")
                    logger.error(f"Failed to get account info for user {user_id}")
                    
    except aiohttp.ClientError as e:
        await event.respond("❌ **Network error:** Unable to connect to account service")
        logger.error(f"Network error in account_info for user {event.sender_id}: {e}")
        
    except json.JSONDecodeError as e:
        await event.respond("❌ **Error:** Invalid response from account service")
        logger.error(f"JSON decode error in account_info for user {event.sender_id}: {e}")
        
    except Exception as e:
        await event.respond(f"❌ **Unexpected error:** {str(e)}")
        logger.error(f"Unexpected error in account_info for user {event.sender_id}: {e}")