from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, Application
import logging
import signal
import asyncio
import sys
from handlers.message_handler import handle_message
import os
from dotenv import load_dotenv
from scheduler import schedule_daily_message

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global app instance
app = None

async def post_init(application: Application):
    load_dotenv()
    TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
    schedule_daily_message(application.bot, TARGET_CHAT_ID)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I do apologize, but I seem to have encountered an error. Please try again in a moment."
        )

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, initiating graceful shutdown...")
    if app:
        app.stop()
    sys.exit(0)

def main():
    global app
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN")

        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN is missing from the .env file.")

        app = (ApplicationBuilder()
               .token(BOT_TOKEN)
               .post_init(post_init)
               .build())

        # Add handlers
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_message))
        app.add_error_handler(error_handler)

        logger.info("🟢 Lennard 2.0 is now listening for group mentions...")
        app.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()


