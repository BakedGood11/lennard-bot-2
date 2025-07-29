# handlers/message_handler.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
import random
from datetime import datetime, timedelta, timezone
import pytz

from telegram import Update
from telegram.ext import ContextTypes

from llm.responder import generate_sassy_reply, summarize_messages
from llm.search import search_brave
from llm.formatter import format_search_response
from llm.dice import handle_dice_roll

from db.connection import insert_message_to_db, fetch_messages_between


def parse_time_window(text: str):
    ph_tz = pytz.timezone("Asia/Manila")
    now = datetime.now(ph_tz)

    # Example: "summarize last 2 hours"
    match = re.search(r"last (\d+) (minute|hour|day)s?", text.lower())
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        delta = {
            "minute": timedelta(minutes=amount),
            "hour": timedelta(hours=amount),
            "day": timedelta(days=amount),
        }[unit]
        return (now - delta, now)

    # Extend later with "from X to Y" patterns
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    # Ignore messages older than 30s
    if update.message.date < datetime.now(timezone.utc) - timedelta(seconds=30):
        return

    user = message.from_user
    text = message.text.strip()
    chat_id = message.chat.id
    username = user.username or user.first_name
    bot_username = context.bot.username.lower()

    is_mention = f"@{bot_username}" in text.lower()
    is_reply_to_bot = (
        message.reply_to_message and
        message.reply_to_message.from_user.username and
        message.reply_to_message.from_user.username.lower() == bot_username
    )

    # Skip if it's a bot message
    if user.is_bot:
        return

    # Log every message to DB
    insert_message_to_db(
        title=username,
        content=text,
        source=str(chat_id)
    )

    # --- Summarization Trigger ---
    if is_mention and ("summarize" in text.lower() or "tl;dr" in text.lower()):
        window = parse_time_window(text)
        if window:
            start_dt, end_dt = window
        else:
            now = datetime.now(pytz.timezone('Asia/Manila'))
            start_dt = now - timedelta(hours=3)
            end_dt = now

        start_utc = start_dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        end_utc = end_dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

        messages = fetch_messages_between(start_utc, end_utc, str(chat_id))
        message_texts = [msg["content"] for msg in messages]

        if message_texts:
            summary = summarize_messages(message_texts)
            await message.reply_text(summary)
        else:
            await message.reply_text("Nothing but foolish prattle to summarize.")
        return

    # --- Search Trigger ---
    if text.lower().startswith("!search") or "google" in text.lower():
        query = re.sub(r"^.*!search", "", text, flags=re.IGNORECASE).strip()
        if not query:
            await message.reply_text("Precious, give us something to search!", parse_mode="Markdown")
            return

        print(f"🔍 Search for Precious: {query}")
        results = search_brave(query)
        print(f"🔎 Search shadows: {results}")

        if not results:
            await message.reply_text("Our nets catch nothing. Blame the hobbits!", parse_mode="Markdown")
            return

        try:
            reply = format_search_response(results)
        except Exception as e:
            print(f"[Format Error] {e}, falling back.")
            reply = "\n".join([f"[{title}]({url})" for title, url, _ in results])

        await message.reply_text(reply, parse_mode="Markdown")
        return

    # --- Bot Mention Trigger ---
    if is_mention or is_reply_to_bot:
        user_input = re.sub(f"@{bot_username}", "", text, flags=re.IGNORECASE).strip()
        print(f"💬 Precious mention by {username}: {user_input}")
        if not user_input:
            await message.reply_text("You called us, but said nothing, precious? Typical.")
            return

        # Dice rolls
        dice = handle_dice_roll(user_input)
        if dice:
            await context.bot.send_message(
                chat_id=chat_id,
                text=dice,
                reply_to_message_id=message.message_id
            )
            return

        # Gollum/Smeagol reply
        reply = generate_sassy_reply(user_input, username)
        await message.reply_text(reply)
        return

    # --- Random Gollum/Smeagol Phrases (3% chance) ---
    random_phrases_bank1 = [
        "Smeagol waits for kind words, yesss.",
        "We remembers happier times, preciousssss.",
        "Do not fear, Smeagol will guides you.",
        "Precious believes in you, yess precious.",
        "Quiet now, Smeagol listens... patiently.",
        "You can do it, precious one!",
    ]
    if random.random() < 0.03:
        await message.reply_text(random.choice(random_phrases_bank1))
        return

    # --- Random Allen-themed Insults (8% chance) ---
    random_phrases_bank2 = [
        "Allen will throw you into Mount Doom for that!",
        "Even Allen knew better than to bother us with nonsense like this.",
        "Gollum!",
        "Allen persevered through worse than your petty prattle.",
        "Allen!",
    ]
    if random.random() < 0.05:
        await message.reply_text(random.choice(random_phrases_bank2))
        return
