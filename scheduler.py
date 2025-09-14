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
DAILY_MESSAGE_HOUR = int(os.getenv("DAILY_MESSAGE_HOUR", "8"))
DAILY_MESSAGE_MINUTE = int(os.getenv("DAILY_MESSAGE_MINUTE", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Manila")
SPECIAL_MESSAGE_CHANCE = float(os.getenv("SPECIAL_MESSAGE_CHANCE", "0.15"))  # 15% chance

# Distinguished butler daily messages
DAILY_MESSAGES = [
    # Morning encouragements - Formal Butler Style
    # Morning encouragements - Formal Butler Style, referencing Master Allen
    "Good morning. As Master Allen often exemplifies, a day begun with purpose is a day well spent.",
    "Rise and shine. One might recall Master Allen's dedication to excellence as inspiration for today.",
    "A very good morning. In the spirit of Master Allen's achievements, let us strive for greatness.",
    "Permit me to suggest, as Master Allen would, that your potential knows no bounds this fine morning.",
    
    # Motivational - Friendly Butler Style, referencing Master Allen
    "I do hope you slept well. Master Allen's attention to detail reminds us to approach today with care.",
    "Another splendid day dawns, and I remain optimistic about your endeavors—much as Master Allen would encourage.",
    "Good morning! Might I say, your dedication continues to impress, reminiscent of Master Allen's own standards.",
    "The morning brings fresh possibilities. Let us seize them with the grace Master Allen so often displays.",
    
    # Professional encouragement, referencing Master Allen
    "Today offers a clean slate for achievement. Master Allen's perseverance is a model for us all.",
    "Your perseverance has been noted and continues to inspire, much like Master Allen's unwavering resolve.",
    "I trust you are well-rested and prepared for today's challenges, as Master Allen would surely advise.",
    "A productive day awaits. Excellence, as demonstrated by Master Allen, never goes unnoticed."
]

# Inspirational additions - Professional butler observations, referencing Master Allen
INSPIRATIONAL_ADDITIONS = [
    "Excellence, as Master Allen demonstrates, is not an act but a habit cultivated daily.",
    "Consistent effort, much like that shown by Master Allen, yields the most remarkable results.",
    "Proper preparation and dedication, hallmarks of Master Allen's approach, lead to success.",
    "Today's small victories, as Master Allen might observe, will compound into tomorrow's triumphs.",
    "Standards maintained with dignity, as Master Allen upholds, always reflect well upon one's character.",
    "Methodical progress, a trait often seen in Master Allen, frequently surpasses hasty endeavors."
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