from telethon import events
from utils.logger import setup_logger
from app.core.backend_config import Settings
from app.utils.coingecko import CoinGeckoClient
from app.utils.gemini import GeminiClient

config = Settings()
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
            # Fetch Tether (USDT) data first (this should work)
            tether_data = {}
            try:
                tether_price_data = coingecko_client.get_simple_price(
                    ids='tether',
                    vs_currencies='usd',
                    include_24hr_change=True,
                    include_24hr_vol=True
                )
                tether_data = tether_price_data.get('tether', {})
                logger.info(f"Tether data fetched: {tether_data}")
            except Exception as tether_error:
                logger.error(f"Error fetching Tether: {tether_error}")
            
            # Try to fetch Somnia data - since it might not be on CoinGecko, we'll handle this gracefully
            somnia_data = {}
            somnia_ids_to_try = ['somnia', 'somnia-network', 'somnia-coin']
            
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
            tether_price = tether_data.get('usd', 'N/A')
            tether_change = tether_data.get('usd_24h_change', 'N/A')
            tether_volume = tether_data.get('usd_24h_vol', 'N/A')
            
            somnia_price = somnia_data.get('usd', 'N/A')
            somnia_change = somnia_data.get('usd_24h_change', 'N/A')
            somnia_volume = somnia_data.get('usd_24h_vol', 'N/A')
            
            # Check if we got at least some valid data
            if tether_price == 'N/A' and somnia_price in ['N/A', 'Not Listed']:
                await event.respond("❌ **Error:** Unable to fetch any price data from CoinGecko")
                return
            
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            await event.respond("❌ **Error:** Failed to fetch market data")
            return
        
        # Prepare prompt for Gemini
        if somnia_price == 'Not Listed':
            prompt = f"""
You are a cryptocurrency trading advisor. I have market data for Tether (USDT) but Somnia is not currently listed on major exchanges like CoinGecko.

Available Market Data:
- Tether (USDT) Price: ${tether_price}
- Tether 24h Change: {tether_change}%
- Tether 24h Volume: ${tether_volume} (if available)

- Somnia: Not listed on major exchanges yet

Given that Somnia is not yet listed on major exchanges, provide advice on:
1. Whether it's wise to hold USDT while waiting for Somnia listings
2. General advice about investing in unlisted/new tokens
3. Risk management strategies for early-stage projects

Keep the response concise but informative (max 200 words).
Format your response with emojis and make it easy to read for a Telegram message.
"""
        else:
            prompt = f"""
You are a cryptocurrency trading advisor. Based on the following market data, provide a trading recommendation.

Current Market Data:
- Tether (USDT) Price: ${tether_price}
- Tether 24h Change: {tether_change}%
- Tether 24h Volume: ${tether_volume} (if available)

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

**Current Prices:**
• Tether (USDT): ${tether_price}
• Somnia: ${somnia_price}

**24h Changes:**
• Tether: {tether_change}%
• Somnia: {somnia_change}%

**AI Recommendation:**
{gemini_response}

⚠️ **Disclaimer:** This is AI-generated advice for informational purposes only. Always do your own research and consider your risk tolerance before trading."""
            
            await event.respond(response_text)
            logger.info(f"Exchange suggestion provided to user {event.sender_id}")
            
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            
            # Fallback response with just market data
            fallback_response = f"""📊 **Market Data**

**Current Prices:**
• Tether (USDT): ${tether_price} ({tether_change}% 24h)
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
    help_text = """"""
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")

@events.register(events.NewMessage(pattern='/auto_exchange_off'))
async def auto_exchange_off(event: events.NewMessage.Event):
    help_text = """"""
    await event.respond(help_text)
    logger.info(f"Help command from user {event.sender_id}")
