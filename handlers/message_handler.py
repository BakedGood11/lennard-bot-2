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

from llm.responder import generate_butler_reply, summarize_messages, split_message
from llm.search import search_brave
from llm.formatter import format_search_response
from llm.dice import handle_dice_roll

from db.connection import insert_message_to_db, fetch_messages_between


def parse_time_window(text: str):
    """Parse time window expressions from text with proper timezone handling."""
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all messages in group chats."""
    if not update.message or not update.message.text:
        return

    message = update.message
    text = message.text
    user = message.from_user
    username = user.first_name if user else "Unknown User"
    chat_id = message.chat.id
    bot_username = context.bot.username.lower()

    # Log every message to database regardless of mention
    try:
        await insert_message_to_db(
            msg_type="text",
            date=message.date.strftime('%Y-%m-%d %H:%M:%S'),
            date_unixtime=int(message.date.timestamp()),
            sender_name=username,
            sender_id=str(user.id) if user else None,
            text=text
        )
    except Exception as e:
        print(f"[DB Error] Failed to log message: {e}")

    # --- Proper mention detection ---
    is_mention = any(
        ent.type == "mention"
        and text[ent.offset: ent.offset + ent.length].lower() == f"@{bot_username}"
        for ent in (message.entities or [])
    )

    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.username
        and message.reply_to_message.from_user.username.lower() == bot_username
    )

    # Only process commands if bot was mentioned or replied to
    if not (is_mention or is_reply_to_bot):
        return

    # --- Normalize user input (strip bot mention) ---
    cleaned_text = re.sub(f"@{bot_username}", "", text, flags=re.IGNORECASE).strip()

    # --- Handle Search Queries ---
    query = None
    lowered = cleaned_text.lower()

    if lowered.startswith("!search "):
        query = cleaned_text[8:].strip()
    elif lowered.startswith("search "):
        query = cleaned_text[6:].strip()
    elif "google" in lowered:
        query = re.sub(r".*google\s*", "", cleaned_text, flags=re.IGNORECASE).strip()

    if query:
        try:
            results = search_brave(query)
            formatted = format_search_response(results)
            for chunk in split_message(formatted):
                await message.reply_text(chunk, parse_mode="MarkdownV2")
        except Exception as e:
            print(f"[Search Error] {e}")
            await message.reply_text(
                "I apologize, but I encountered an error processing your search request.",
                parse_mode="Markdown"
            )
        return
    
    # --- Handle Summarization ---
    if "summarize" in cleaned_text.lower() or "tl;dr" in cleaned_text.lower():
        window = parse_time_window(cleaned_text)
        if not window:
            now = datetime.now(pytz.timezone('Asia/Manila'))
            window = (now - timedelta(hours=3), now)

        start_dt, end_dt = window
        try:
            messages = await fetch_messages_between(
                start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                str(chat_id)
            )
            if messages:
                summary = await summarize_messages(messages)
                await message.reply_text(f"Very good, {username}. Here is your requested summary:\n\n{summary}")
            else:
                await message.reply_text(
                    "I regret to inform you that there are no messages to summarize from the specified timeframe, sir."
                )
        except Exception as e:
            print(f"[Summarization Error] {e}")
            await message.reply_text(
                "I apologize, but I encountered an issue while preparing your summary. Please try again."
            )
        return

    # --- Handle Empty Mentions ---
    if not cleaned_text:
        await message.reply_text(f"You rang, {username}? How may I be of service?")
        return

    # --- Handle Dice Rolls ---
    dice = handle_dice_roll(cleaned_text)
    if dice:
        await message.reply_text(f"Certainly, {username}. {dice}")
        return

    # --- Handle General Butler Replies ---
    try:
        reply = generate_butler_reply(cleaned_text, username)
        await message.reply_text(reply)
    except Exception as e:
        print(f"[Reply Error] {e}")
        await message.reply_text(
            "I beg your pardon, but I seem to be having difficulty responding at the moment."
        )
