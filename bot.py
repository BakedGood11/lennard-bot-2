from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from handlers.message_handler import handle_message
import os
from dotenv import load_dotenv
from scheduler import schedule_daily_message

async def post_init(app):
    TARGET_CHAT_ID = -1001139716672
    schedule_daily_message(app.bot, TARGET_CHAT_ID)

def main():
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing from the .env file.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handle all text messages in group chats
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_message))

    print("🟢 Lennard 2.0 is now listening for group mentions...")
    app.run_polling()

if __name__ == "__main__":
    main()
