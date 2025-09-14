from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import logging
import os
import asyncio
from pytz import timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration constants
DAILY_MESSAGE_HOUR = int(os.getenv("DAILY_MESSAGE_HOUR", "10"))
DAILY_MESSAGE_MINUTE = int(os.getenv("DAILY_MESSAGE_MINUTE", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Manila")
SPECIAL_MESSAGE_CHANCE = float(os.getenv("SPECIAL_MESSAGE_CHANCE", "0.15"))  # 15% chance

# Distinguished butler daily messages
DAILY_MESSAGES = [
    # Morning encouragements - Formal Butler Style
    "Good morning, sir. I trust this day shall bring you great success and satisfaction.",
    "Rise and shine, if you will. Today presents numerous opportunities for excellence.",
    "A very good morning to you. I have every confidence you shall accomplish great things today.",
    "Good day, sir. Permit me to suggest that your potential knows no bounds this fine morning.",
    
    # Motivational - Friendly Butler Style  
    "I do hope you slept well, sir. Today awaits your distinguished attention.",
    "Another splendid day dawns, and I remain optimistic about your endeavors.",
    "Good morning! Might I say, your dedication continues to impress, sir.",
    "The morning brings fresh possibilities. I trust you shall seize them with your usual grace.",
    
    # Professional encouragement
    "Today offers a clean slate for achievement, sir. I have complete faith in your abilities.",
    "Good morning. Your perseverance has been noted and continues to inspire, if I may say so.",
    "I trust you are well-rested and prepared for today's challenges, sir.",
    "A productive day awaits, I am certain. Your attention to excellence never goes unnoticed."
]

# Inspirational additions - Professional butler observations
INSPIRATIONAL_ADDITIONS = [
    "Excellence, as they say, is not an act but a habit cultivated daily.",
    "I am reminded that consistent effort yields the most remarkable results, sir.",
    "Proper preparation and dedication have always been the hallmarks of success.",
    "May I suggest that today's small victories will compound into tomorrow's triumphs.",
    "Standards maintained with dignity always reflect well upon one's character.",
    "I have observed that methodical progress often surpasses hasty endeavors, sir."
]


def schedule_daily_message(bot, chat_id: int):
    """
    Schedule a daily check-in message in dignified butler style at the configured time.
    
    Args:
        bot: Telegram bot instance
        chat_id: Target chat ID for daily messages
    """
    scheduler = AsyncIOScheduler()
    
    async def daily_message_job():
        """Send the daily butler message."""
        try:
            # Select primary encouraging message
            message = random.choice(DAILY_MESSAGES)
            
            # Add inspirational addition with configured probability
            if random.random() < SPECIAL_MESSAGE_CHANCE:
                additional_wisdom = random.choice(INSPIRATIONAL_ADDITIONS)
                message += f"\n\n{additional_wisdom}"
            
            logger.info(f"Butler: sending daily message to chat {chat_id}")
            
            await bot.send_message(chat_id=chat_id, text=message)
            logger.info("Daily butler message sent successfully")
            
        except Exception as e:
            logger.error(f"Butler scheduler error sending daily message: {e}")
            
            # Attempt to send a fallback message
            try:
                fallback_message = "Good morning, sir. I trust you are well, despite my technical difficulties."
                await bot.send_message(chat_id=chat_id, text=fallback_message)
                logger.info("Fallback message sent successfully")
            except Exception as fallback_error:
                logger.error(f"Failed to send fallback message: {fallback_error}")
    
    # Schedule the job
    try:
        trigger = CronTrigger(
            hour=DAILY_MESSAGE_HOUR, 
            minute=DAILY_MESSAGE_MINUTE, 
            timezone=timezone(TIMEZONE)
        )
        scheduler.add_job(daily_message_job, trigger)
        scheduler.start()
        
        logger.info(f"Daily butler message scheduled for {DAILY_MESSAGE_HOUR:02d}:{DAILY_MESSAGE_MINUTE:02d} {TIMEZONE}")
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to schedule daily message: {e}")
        raise


def get_random_daily_message() -> str:
    """
    Generate a random daily message for testing purposes.
    
    Returns:
        str: A formatted daily message in butler style
    """
    message = random.choice(DAILY_MESSAGES)
    
    if random.random() < SPECIAL_MESSAGE_CHANCE:
        additional_wisdom = random.choice(INSPIRATIONAL_ADDITIONS)
        message += f"\n\n{additional_wisdom}"
    
    return message


# Standalone testing functionality
if __name__ == "__main__":
    from telegram import Bot
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))
    
    if not TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        exit(1)
    
    if CHAT_ID == 0:
        logger.error("TARGET_CHAT_ID not found or invalid in environment variables")
        exit(1)
    
    bot = Bot(token=TOKEN)
    
    async def test_daily_message():
        """Test function to send a sample daily message."""
        try:
            message = get_random_daily_message()
            logger.info(f"Testing daily message: {message}")
            
            await bot.send_message(chat_id=CHAT_ID, text=message)
            logger.info("Test message sent successfully!")
            
        except Exception as e:
            logger.error(f"Failed to send test message: {e}")
    
    # Run the test
    try:
        asyncio.run(test_daily_message())
    except Exception as e:
        logger.error(f"Test execution failed: {e}")