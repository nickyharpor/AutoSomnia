from telethon import events
import sys
import os
import aiohttp
import json
import time

# Add the parent directory to the path to import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.backend_config import settings
from app.utils.coingecko import CoinGeckoClient
from app.utils.gemini import GeminiClient

# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.logger import setup_logger # ignore
from config.bot_config import Config


config = Config()
logger = setup_logger(config.LOG_LEVEL)

@events.register(events.NewMessage(pattern='/suggest_exchange'))
async def suggest_exchange(event: events.NewMessage.Event):
    """Get trading suggestion from Gemini AI based on current market data."""
    try:
        await event.respond("🔍 **Analyzing market data...**")
        
        # Initialize clients
        coingecko_client = CoinGeckoClient()
        gemini_client = GeminiClient()
        
        # Get price data from CoinGecko
        try:
            # Try to fetch Somnia data - since it might not be on CoinGecko, we'll handle this gracefully
            somnia_data = {}
            somnia_ids_to_try = ['somnia']
            
            for somnia_id in somnia_ids_to_try:
                try:
                    somnia_price_data = coingecko_client.get_simple_price(
                        ids=somnia_id,
                        vs_currencies='usd',
                        include_24hr_change=True,
                        include_24hr_vol=True
                    )
                    if somnia_price_data and somnia_id in somnia_price_data:
                        somnia_data = somnia_price_data[somnia_id]
                        logger.info(f"Somnia data fetched with ID '{somnia_id}': {somnia_data}")
                        break
                except Exception as somnia_error:
                    logger.warning(f"Failed to fetch Somnia with ID '{somnia_id}': {somnia_error}")
                    continue
            
            # If Somnia is not found on CoinGecko, use placeholder data
            if not somnia_data:
                logger.info("Somnia not found on CoinGecko, using placeholder data")
                somnia_data = {
                    'usd': 'Not Listed',
                    'usd_24h_change': 'N/A',
                    'usd_24h_vol': 'N/A'
                }
            
            # Extract data
            somnia_price = somnia_data.get('usd', 'N/A')
            somnia_change = somnia_data.get('usd_24h_change', 'N/A')
            somnia_volume = somnia_data.get('usd_24h_vol', 'N/A')
            
            # Check if we got at least some valid data
            if somnia_price in ['N/A', 'Not Listed']:
                await event.respond("❌ **Error:** Unable to fetch any price data from CoinGecko")
                return
            
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            await event.respond("❌ **Error:** Failed to fetch market data")
            return
        
        # Prepare prompt for Gemini
        prompt = f"""
You are a cryptocurrency trading advisor. Based on the following market data, provide a trading recommendation.

Current Market Data:
- Tether (USDT) Price: $1
- Tether 24h Change: 0%

- Somnia Price: ${somnia_price}
- Somnia 24h Change: {somnia_change}%
- Somnia 24h Volume: ${somnia_volume} (if available)

Please analyze this data and provide a recommendation on whether it's a good time to:
1. Buy Tether using Somnia
2. Buy Somnia using Tether
3. Hold current positions (no trade recommended)

Consider factors like:
- Price trends and momentum
- 24-hour price changes
- Market volatility
- Risk management

Provide a clear recommendation with reasoning. Keep the response concise but informative (max 200 words).
Format your response with emojis and make it easy to read for a Telegram message.
"""
        
        # Get AI recommendation from Gemini
        try:
            await event.respond("🤖 **Getting AI analysis...**")
            
            gemini_response = await gemini_client.generate_response(prompt)
            
            # Format the response
            response_text = f"""📊 **Trading Suggestion**

• Somnia Current Price: ${somnia_price}
• Somnia 24h Change: {somnia_change}%

**AI Recommendation:**
{gemini_response}

⚠️ **Disclaimer:** This is AI-generated advice for informational purposes only. Always do your own research and consider your risk tolerance before trading."""
            
            await event.respond(response_text)
            logger.info(f"Exchange suggestion provided to user {event.sender_id}")
            
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            
            # Fallback response with just market data
            fallback_response = f"""📊 **Market Data**

• Somnia: ${somnia_price} ({somnia_change}% 24h)

❌ **AI analysis temporarily unavailable**

💡 **General Guidelines:**
• Consider buying when prices are down significantly
• Take profits when prices are up significantly
• Always manage your risk and don't invest more than you can afford to lose

⚠️ **Always do your own research before trading!**"""
            
            await event.respond(fallback_response)
            
    except Exception as e:
        logger.error(f"Unexpected error in suggest_exchange: {e}")
        await event.respond("❌ **Error:** Something went wrong while analyzing the market. Please try again later.")

@events.register(events.NewMessage(pattern='/auto_exchange_on'))
async def auto_exchange_on(event: events.NewMessage.Event):
    text = """Auto exchange is now ON for your account. AutoSomnia will trade for you wisely and timely.

👉 You can stop auto exchange with /auto_exchange_off
    
⚠️ **You must have at least one account with some funds in it, otherwise nothing happens!**

💸 Create a /new_account and fund it if you've not done it so far."""
    await event.respond(text)
    logger.info(f"Auto exchange on from user {event.sender_id}")

@events.register(events.NewMessage(pattern='/auto_exchange_off'))
async def auto_exchange_off(event: events.NewMessage.Event):
    text = """Auto exchange is now OFF for your account. AutoSomnia won't trade on your behalf.

    👉 You can start auto exchange with /auto_exchange_on"""
    await event.respond(text)
    logger.info(f"Auto exchange off from user {event.sender_id}")

@events.register(events.NewMessage(pattern=r'/buy_usd\s+(\S+)(?:\s+(\S+))?'))
async def buy_usd(event: events.NewMessage.Event):
    """Buy SUSDT (USD) tokens using ETH via exchange swap."""
    try:
        amount = event.pattern_match.group(1).strip()
        address = event.pattern_match.group(2)
        if address:
            address = address.strip()
        
        user_id = event.sender_id
        
        await event.respond("🔄 **Preparing USD purchase...**")
        
        # Get user's account from database to get private key
        async with aiohttp.ClientSession() as session:
            # First, get user's accounts
            async with session.get(
                f"{config.API_BASE_URL}/account/list_user_accounts/{user_id}"
            ) as response:
                
                if response.status != 200:
                    await event.respond("❌ **Error:** Unable to retrieve your accounts")
                    return
                
                data = await response.json()
                accounts = data.get("accounts", [])
                
                if not accounts:
                    await event.respond("❌ **No accounts found.** Create an account first with /new_account")
                    return
                
                # Use the first account or specified address
                account = None
                if address:
                    # Find account with matching address
                    for acc in accounts:
                        if acc["address"].lower() == address.lower():
                            account = acc
                            break
                    if not account:
                        await event.respond(f"❌ **Account not found:** {address}")
                        return
                else:
                    account = accounts[0]
                
                private_key = account["private_key"]
                from_address = account["address"]
                
                # Prepare swap parameters
                # Path: ETH -> SUSDT (WETH -> SUSDT)
                path = [settings.WSTT, settings.SUSDT]  # WSTT (wrapped ETH) -> SUSDT
                deadline = int(time.time()) + 300  # 5 minutes from now
                
                await event.respond("💱 **Executing SOMI to USD swap...**")
                
                # Prepare the swap request
                swap_payload = {
                    "amount_in": int(float(amount) * 10**18),  # Convert ETH to wei
                    "amount_out_min": int(float(amount) * 10**6),  # Minimum SUSDT (assuming 6 decimals)
                    "path": path,
                    "to": from_address,
                    "deadline": deadline,
                    "from_address": from_address,
                    "private_key": private_key
                }
                
                # Add eth_value for ETH swap
                eth_value = int(float(amount) * 10**18)  # ETH amount in wei
                
                # Make API call to swap ETH for tokens
                async with session.post(
                    f"{config.API_BASE_URL}/exchange/swap-exact-eth-for-tokens",
                    json=swap_payload,
                    params={"eth_value": eth_value},
                    headers={"Content-Type": "application/json"}
                ) as swap_response:
                    
                    if swap_response.status == 200:
                        swap_data = await swap_response.json()
                        
                        response_text = f"""✅ **USD Purchase Successful!**

📤 **From:** `{from_address}`
💰 **SOM Spent:** {amount} SOM
💵 **USD Tokens Received:** ~{amount} SUSDT
🔗 **Transaction Hash:** `{swap_data['transaction_hash']}`
⛽ **Gas Used:** {swap_data['gas_used']}

🔍 **Transaction is being processed on the blockchain...**

💡 **Tip:** Use `/account_info` to check your updated balances"""
                        
                        await event.respond(response_text)
                        logger.info(f"USD purchase successful: {swap_data['transaction_hash']} by user {user_id}")
                        
                    else:
                        error_data = await swap_response.json()
                        error_msg = error_data.get("detail", "Unknown error occurred")
                        await event.respond(f"❌ **USD purchase failed:** {error_msg}")
                        logger.error(f"USD purchase failed for user {user_id}: {error_msg}")

    except json.JSONDecodeError as e:
        await event.respond("❌ **Error:** Invalid response from exchange service")
        logger.error(f"JSON decode error in buy_usd for user {event.sender_id}: {e}")

    except ValueError as ve:
        await event.respond(f"❌ **Invalid amount:** Please provide a valid number")
        logger.error(f"Invalid amount in buy_usd for user {event.sender_id}: {ve}")
        
    except aiohttp.ClientError as e:
        await event.respond("❌ **Network error:** Unable to connect to exchange service")
        logger.error(f"Network error in buy_usd for user {event.sender_id}: {e}")

    except Exception as e:
        await event.respond(f"❌ **Unexpected error:** {str(e)}")
        logger.error(f"Unexpected error in buy_usd for user {event.sender_id}: {e}")


@events.register(events.NewMessage(pattern='/buy_usd'))
async def buy_usd_help(event):
    """Show help for buy_usd command when no parameters provided"""
    help_text = """💵 **Buy USD Help**

**Usage:**
• `/buy_usd <amount>` - Buy USD tokens with ETH from your first account
• `/buy_usd <amount> <address>` - Buy USD tokens with ETH from specific account

**Examples:**
• `/buy_usd 0.1` - Buy ~0.1 USD worth using 0.1 ETH
• `/buy_usd 0.5 0x742d35Cc6634C0532925a3b8D4C9db96590c6C87` - Buy from specific account

**How it works:**
• Swaps your SOMI for SUSDT (USD stablecoin) on Somnia
• Uses current market rates for the exchange
• Minimum slippage protection included

⚠️ **Note:** Make sure you have enough SOMI in your account for the swap + gas fees"""
    
    await event.respond(help_text)
    logger.info(f"Buy USD help shown to user {event.sender_id}")


@events.register(events.NewMessage(pattern=r'/sell_usd\s+(\S+)(?:\s+(\S+))?'))
async def sell_usd(event: events.NewMessage.Event):
    """Sell SUSDT (USD) tokens for ETH via exchange swap."""
    try:
        amount = event.pattern_match.group(1).strip()
        address = event.pattern_match.group(2)
        if address:
            address = address.strip()
        
        user_id = event.sender_id
        
        await event.respond("🔄 **Preparing USD sale...**")
        
        # Get user's account from database to get private key
        async with aiohttp.ClientSession() as session:
            # First, get user's accounts
            async with session.get(
                f"{config.API_BASE_URL}/account/list_user_accounts/{user_id}"
            ) as response:
                
                if response.status != 200:
                    await event.respond("❌ **Error:** Unable to retrieve your accounts")
                    return
                
                data = await response.json()
                accounts = data.get("accounts", [])
                
                if not accounts:
                    await event.respond("❌ **No accounts found.** Create an account first with /new_account")
                    return
                
                # Use the first account or specified address
                account = None
                if address:
                    # Find account with matching address
                    for acc in accounts:
                        if acc["address"].lower() == address.lower():
                            account = acc
                            break
                    if not account:
                        await event.respond(f"❌ **Account not found:** {address}")
                        return
                else:
                    account = accounts[0]
                
                private_key = account["private_key"]
                from_address = account["address"]
                
                # Prepare swap parameters
                # Path: SUSDT -> ETH (SUSDT -> WETH)
                path = [settings.SUSDT, settings.WSTT]  # SUSDT -> WSTT (wrapped ETH)
                deadline = int(time.time()) + 300  # 5 minutes from now
                
                await event.respond("💱 **Executing USD to SOMI swap...**")
                
                # Prepare the swap request
                swap_payload = {
                    "amount_in": int(float(amount) * 10**6),  # Convert USD to SUSDT units (6 decimals)
                    "amount_out_min": int(float(amount) * 0.95 * 10**18),  # Minimum ETH with 5% slippage (18 decimals)
                    "path": path,
                    "to": from_address,
                    "deadline": deadline,
                    "from_address": from_address,
                    "private_key": private_key
                }
                
                # Make API call to swap tokens for ETH
                async with session.post(
                    f"{config.API_BASE_URL}/exchange/swap-exact-tokens-for-eth",
                    json=swap_payload,
                    headers={"Content-Type": "application/json"}
                ) as swap_response:
                    
                    if swap_response.status == 200:
                        swap_data = await swap_response.json()
                        
                        response_text = f"""✅ **USD Sale Successful!**

📤 **From:** `{from_address}`
💵 **USD Tokens Sold:** {amount} SUSDT
💰 **SOM Received:** ~{amount} SOM
🔗 **Transaction Hash:** `{swap_data['transaction_hash']}`
⛽ **Gas Used:** {swap_data['gas_used']}

🔍 **Transaction is being processed on the blockchain...**

💡 **Tip:** Use `/account_info` to check your updated balances"""
                        
                        await event.respond(response_text)
                        logger.info(f"USD sale successful: {swap_data['transaction_hash']} by user {user_id}")
                        
                    else:
                        error_data = await swap_response.json()
                        error_msg = error_data.get("detail", "Unknown error occurred")
                        await event.respond(f"❌ **USD sale failed:** {error_msg}")
                        logger.error(f"USD sale failed for user {user_id}: {error_msg}")

    except json.JSONDecodeError as e:
        await event.respond("❌ **Error:** Invalid response from exchange service")
        logger.error(f"JSON decode error in sell_usd for user {event.sender_id}: {e}")

    except ValueError as ve:
        await event.respond(f"❌ **Invalid amount:** Please provide a valid number")
        logger.error(f"Invalid amount in sell_usd for user {event.sender_id}: {ve}")
        
    except aiohttp.ClientError as e:
        await event.respond("❌ **Network error:** Unable to connect to exchange service")
        logger.error(f"Network error in sell_usd for user {event.sender_id}: {e}")

    except Exception as e:
        await event.respond(f"❌ **Unexpected error:** {str(e)}")
        logger.error(f"Unexpected error in sell_usd for user {event.sender_id}: {e}")


@events.register(events.NewMessage(pattern='/sell_usd'))
async def sell_usd_help(event):
    """Show help for sell_usd command when no parameters provided"""
    help_text = """💰 **Sell USD Help**

**Usage:**
• `/sell_usd <amount>` - Sell USD tokens for SOMI from your first account
• `/sell_usd <amount> <address>` - Sell USD tokens for SOMI from specific account

**Examples:**
• `/sell_usd 0.1` - Sell 0.1 SUSDT for ~0.1 SOM
• `/sell_usd 0.5 0x742d35Cc6634C0532925a3b8D4C9db96590c6C87` - Sell from specific account

**How it works:**
• Swaps your SUSDT (USD stablecoin) for SOMI on Somnia
• Uses current market rates for the exchange
• 5% slippage protection included for price fluctuations

⚠️ **Note:** Make sure you have enough SUSDT tokens in your account for the swap + gas fees"""
    
    await event.respond(help_text)
    logger.info(f"Sell USD help shown to user {event.sender_id}")

