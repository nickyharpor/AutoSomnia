import asyncio
import signal
from typing import Optional

from telethon import TelegramClient
from telethon.errors import RPCError

from config.bot_config import Config
from utils.logger import setup_logger
from handlers import basic_handlers, account_handlers, exchange_handlers

# Initialize logger after config is available
config = Config()
logger = setup_logger(config.LOG_LEVEL)


class TelegramBot:
    """Telegram bot wrapper managing client lifecycle, handlers, and shutdown."""

    def __init__(self) -> None:
        self.config = config  # Use the already initialized config
        self._validate_config()

        self.client: TelegramClient = TelegramClient(
            self.config.SESSION_NAME,
            self.config.API_ID,
            self.config.API_HASH,
        )
        self._stopping = asyncio.Event()

    def _validate_config(self) -> None:
        """Validate required configuration values and fail fast with clear logs."""
        missing = []
        if not getattr(self.config, "API_ID", None):
            missing.append("API_ID")
        if not getattr(self.config, "API_HASH", None):
            missing.append("API_HASH")
        if not getattr(self.config, "BOT_TOKEN", None):
            missing.append("BOT_TOKEN")
        if not getattr(self.config, "SESSION_NAME", None):
            missing.append("SESSION_NAME")
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    def _register_handlers(self) -> None:
        """Attach event handlers to the client."""
        # Basic handlers
        self.client.add_event_handler(basic_handlers.start_handler)
        self.client.add_event_handler(basic_handlers.help_handler)
        self.client.add_event_handler(basic_handlers.echo_handler)
        
        # Account handlers
        self.client.add_event_handler(account_handlers.new_account)
        self.client.add_event_handler(account_handlers.withdraw_funds_handler)
        self.client.add_event_handler(account_handlers.withdraw_funds_help)
        self.client.add_event_handler(account_handlers.account_info)
        
        # Exchange handlers
        self.client.add_event_handler(exchange_handlers.suggest_exchange)
        self.client.add_event_handler(exchange_handlers.auto_exchange_on)
        self.client.add_event_handler(exchange_handlers.auto_exchange_off)
        
        logger.info("Handlers registered: basic, account, and exchange handlers")

    async def start(self) -> None:
        """Start the bot with logging and keep it running until disconnected."""
        logger.info("Starting Telegram bot...")
        try:
            await self.client.start(bot_token=self.config.BOT_TOKEN)
        except RPCError as e:
            logger.error(f"Telegram RPC error during start: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during client start: {e}")
            raise

        self._register_handlers()
        logger.info("Bot started successfully")

        await self.client.run_until_disconnected()

    async def stop(self) -> None:
        """Signal-safe shutdown: disconnect client and mark stopping."""
        if self._stopping.is_set():
            return
        self._stopping.set()
        try:
            if self.client.is_connected():
                await self.client.disconnect()
        except Exception as e:
            logger.warning(f"Error while disconnecting client: {e}")


async def run_with_retries(bot: TelegramBot, retries: int = 3, base_delay: float = 1.0) -> None:
    """Run bot with simple exponential backoff on startup failures."""
    attempt = 0
    while True:
        try:
            await bot.start()
            return
        except Exception as run_with_retries_exception:
            attempt += 1
            if attempt > retries:
                logger.error(f"Failed to start bot after {retries} retries: {run_with_retries_exception}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Startup failed (attempt {attempt}/{retries}). Retrying in {delay:.1f}s...")
            await asyncio.sleep(delay)


async def main() -> None:
    """Application entry: setup signals, run bot, ensure cleanup."""
    bot = TelegramBot()

    main_loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler(sig: Optional[int] = None) -> None:
        logger.info(f"Received signal {sig}. Initiating graceful shutdown...")
        stop_event.set()

    # Register signal handlers where supported (Unix). On Windows, SIGTERM may not be available.
    for s in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if s is not None:
            try:
                main_loop.add_signal_handler(s, _signal_handler, int(s.value) if hasattr(s, "value") else int(s))
            except NotImplementedError:
                # add_signal_handler may not be implemented on some platforms
                pass

    start_task = None
    try:
        # Start bot (with retries) concurrently with waiting for stop signal.
        start_task = asyncio.create_task(run_with_retries(bot))
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise
    finally:
        # Ensure bot is stopped and task is canceled.
        await bot.stop()
        # Cancel start task if still running
        for task in [t for t in [start_task] if 'start_task' in locals() and not t.done()]:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        logger.info("Shutdown complete")


if __name__ == "__main__":
    # Protect against running inside an existing event loop (e.g., notebooks)
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Fallback for cases where an event loop is already running
        logger.warning(f"asyncio.run failed ({e}). Using existing loop fallback.")
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        # Keep the loop alive briefly to start tasks; real hosts should manage the loop lifecycle.
        loop.run_until_complete(asyncio.sleep(0.1))