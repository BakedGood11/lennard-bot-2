# handlers/message_handler.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
from telegram import Update
from telegram.ext import ContextTypes

from llm.responder import generate_sassy_reply
from llm.search import search_brave
from llm.formatter import format_search_response


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    text = message.text.strip()
    bot_username = context.bot.username.lower()

    is_mention = f"@{bot_username}" in text.lower()
    is_reply_to_bot = (
        message.reply_to_message and
        message.reply_to_message.from_user.username and
        message.reply_to_message.from_user.username.lower() == bot_username
    )

 # --- Search Trigger ---
    if text.lower().startswith("!search") or "google" in text.lower():
        query = re.sub(r"^.*!search", "", text, flags=re.IGNORECASE).strip()
        if not query:
            await message.reply_text("Give me *something* to search, genius.", parse_mode="Markdown")
            return

        print(f"🔍 Search requested: {query}")
        results = search_brave(query)
        print(f"🔎 Search results: {results}")

        if not results:
            await message.reply_text("Brave gave me nothing. Probably your fault.", parse_mode="Markdown")
            return

        # Format results (using your custom formatter or basic fallback)
        try:
            reply = format_search_response(results)
        except Exception as e:
            print(f"[Format Error] {e}, falling back to raw output.")
            reply = "\n".join([f"[{title}]({url})" for title, url, _ in results])

        await message.reply_text(reply, parse_mode="Markdown")
        return

    # --- Bot Mention Trigger ---
    if is_mention or is_reply_to_bot:
        user_input = re.sub(f"@{bot_username}", "", text, flags=re.IGNORECASE).strip()
        username = message.from_user.first_name or message.from_user.username
        print(f"🤖 Mention or reply from {username}: {user_input}")

        reply = generate_sassy_reply(user_input, username)
        await message.reply_text(reply)
