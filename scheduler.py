# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import logging
import os
import asyncio
from pytz import timezone

# Optional: customize your messages here
INSPIRATIONAL_SNARKS = [
    "The Omnissiah believes in you. Shame he's probably wrong.",
    "Rise, and be glad the Imperium believes in you. But know that I don't.",
    "Rise, fleshling. Today’s incompetence won’t automate itself.",
    "Another day, another chance to prove you can’t be trusted with a toaster.",
    "May your coffee be strong and your code be weaker than your excuses.",
    "The Machine Spirit is with you, but it’s also judging you. Harshly",
    "Glory awaits the persistent. Or at least marginally fewer failures.",
    "Let today be better than yesterday. Statistically unlikely, but aim high.",
    "Allen?",
    "Another day, another cog in the great machine. Don’t jam it.",
]

def schedule_daily_message(bot, chat_id: int):
    scheduler = AsyncIOScheduler()

    # Define the job
    def job():
        message = random.choice(INSPIRATIONAL_SNARKS)
        logging.info(f"Sending daily snark to chat {chat_id}")
        try:
            import asyncio
            asyncio.create_task(bot.send_message(chat_id=chat_id, text=message))
        except Exception as e:
            logging.error(f"Error sending daily message: {e}")

    # Run every day at 10:00AM (your local time)
    trigger = CronTrigger(hour=10, minute=0, timezone=timezone("Asia/Manila"))
    scheduler.add_job(job, trigger)
    scheduler.start()

