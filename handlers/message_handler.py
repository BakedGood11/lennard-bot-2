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

from llm.responder import generate_sassy_reply, summarize_messages, split_message
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    # Ignore messages older than 30s (using consistent UTC timezone handling)
    utc_now = datetime.now(timezone.utc)
    if update.message.date < utc_now - timedelta(seconds=30):
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
    try:
        insert_message_to_db(
            title=username,
            content=text,
            source=str(chat_id),
            msg_type="text"
        )
    except Exception as e:
        print(f"[DB Error] Failed to log message: {e}")

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

        try:
            messages = fetch_messages_between(start_utc, end_utc, str(chat_id))
            message_texts = [msg["content"] for msg in messages]

            if message_texts:
                summary = summarize_messages(message_texts)
                await message.reply_text(f"Very good, {username}. Here is your requested summary:\n\n{summary}")
            else:
                await message.reply_text("I regret to inform you that there are no messages to summarize from the specified timeframe, sir.")
        except Exception as e:
            print(f"[Summarization Error] {e}")
            await message.reply_text("I apologize, but I encountered an issue while preparing your summary. Please try again.")
        return

    # --- Search Trigger ---
    if text.lower().startswith("!search") or "google" in text.lower():
        query = re.sub(r"^.*!search", "", text, flags=re.IGNORECASE).strip()
        if not query:
            await message.reply_text("Certainly, but might I suggest providing a search query, sir?", parse_mode="Markdown")
            return

        print(f"🔍 Butler search for {username}: {query}")
        
        try:
            results = search_brave(query)
            print(f"🔎 Search results retrieved: {len(results) if results else 0} items")

            if not results:
                await message.reply_text("I'm terribly sorry, but my search has yielded no results. Perhaps we might try a different approach?", parse_mode="Markdown")
                return

            try:
                reply = format_search_response(results)
            except Exception as e:
                print(f"[Format Error] {e}, falling back to simple format.")
                reply = "\n".join([f"[{title}]({url})" for title, url, _ in results])

            # Split into chunks and send
            for chunk in split_message(reply):
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=chunk,
                        parse_mode="MarkdownV2"
                    )
                except Exception as e:
                    print(f"[Send Error] {e}, retrying without parse_mode.")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=chunk  # Retry in plain text if formatting fails
                    )
                    
        except Exception as e:
            print(f"[Search Error] {e}")
            await message.reply_text("I apologize for the inconvenience, but I encountered an issue with your search request.")
        return

    # --- Bot Mention Trigger ---
    if is_mention or is_reply_to_bot:
        user_input = re.sub(f"@{bot_username}", "", text, flags=re.IGNORECASE).strip()
        print(f"💬 Butler mention by {username}: {user_input}")
        if not user_input:
            await message.reply_text(f"You rang, {username}? How may I be of service?")
            return

        # Dice rolls
        dice = handle_dice_roll(user_input)
        if dice:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Certainly, {username}. {dice}",
                reply_to_message_id=message.message_id
            )
            return

        # Butler reply (you'll need to update generate_sassy_reply to generate_butler_reply)
        try:
            reply = generate_sassy_reply(user_input, username)  # This function needs to be updated for butler personality
            await message.reply_text(reply)
        except Exception as e:
            print(f"[Reply Error] {e}")
            await message.reply_text("I beg your pardon, but I seem to be having difficulty responding at the moment.")
        return

    # --- Random Encouraging Butler Phrases (3% chance) ---
    butler_encouragement = [
        "Might I say, you're doing excellently today, sir.",
        "Your presence graces this conversation, if I may say so.",
        "Allow me to remind you that perseverance is a noble virtue.",
        "I have every confidence in your abilities, sir.",
        "A moment of patience, if you would. Good things await.",
        "Your dedication does not go unnoticed, I assure you.",
    ]
    if random.random() < 0.03:
        await message.reply_text(random.choice(butler_encouragement))
        return

    # --- Random Butler Observations (8% chance) ---
    butler_observations = [
        "One must maintain proper decorum in all endeavors.",
        "Excellence is achieved through attention to detail, wouldn't you agree?",
        "*adjusts collar with dignified precision*",
        "A well-ordered approach serves one best, I find.",
        "Indeed, sir. Most enlightening conversation.",
        "Quite right. Standards must be maintained.",
        "As you wish, sir. The matter shall be attended to.",
    ]
    if random.random() < 0.08:  # Fixed the probability to match the comment
        await message.reply_text(random.choice(butler_observations))
        return