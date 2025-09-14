import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """
    Establish connection to the MySQL database using environment variables.
    
    Returns:
        mysql.connector.connection: Database connection object
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"), 
            database=os.getenv("DB_NAME"),
            password=os.getenv("DB_PASS"),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
        return connection
    except mysql.connector.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise


async def insert_message_to_db(msg_type: str, date: str, date_unixtime: int, 
                             sender_name: str, sender_id: str, text: str) -> None:
    """Insert a message into the database."""
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO messages (msg_type, date, date_unixtime, sender_name, sender_id, text)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (msg_type, date, date_unixtime, sender_name, sender_id, text)
        
        cursor.execute(query, values)
        connection.commit()
        
        logging.info(f"Message inserted successfully for {sender_name}")
        
    except Exception as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


async def fetch_messages_between(start_dt, end_dt, chat_id):
    """
    Fetch messages between specified time ranges.
    
    Args:
        start_dt (str): Start datetime in 'YYYY-MM-DD HH:MM:SS' format
        end_dt (str): End datetime in 'YYYY-MM-DD HH:MM:SS' format  
        chat_id (str): Chat ID to filter by (currently unused as we fetch all messages)
        
    Returns:
        list: List of message texts only for summarization
    """
    conn = None
    try:
        conn = get_database_connection()
        with conn.cursor(dictionary=True) as cursor:
            # First, let's check what's in our date range
            check_query = """
                SELECT MIN(date) as earliest, MAX(date) as latest, COUNT(*) as total
                FROM messages
                WHERE date BETWEEN %s AND %s
            """
            cursor.execute(check_query, (start_dt, end_dt))
            stats = cursor.fetchone()
            logger.info(f"Date range check: {stats}")

            # Main query
            query = """
                SELECT sender_name, text, date
                FROM messages 
                WHERE date BETWEEN %s AND %s
                AND text IS NOT NULL
                AND text != ''
                ORDER BY date ASC
            """
            
            cursor.execute(query, (start_dt, end_dt))
            results = cursor.fetchall()
            
            # Debug information
            logger.info(f"Query parameters: start={start_dt}, end={end_dt}")
            logger.info(f"Raw results count: {len(results)}")
            
            # Format messages with sender names
            messages = [f"{row['sender_name']}: {row['text']}" for row in results if row['text']]
            
            logger.info(f"Fetched {len(messages)} messages between {start_dt} and {end_dt}")
            
            # If no messages found, check total message count
            if not messages:
                cursor.execute("SELECT COUNT(*) as total FROM messages")
                total = cursor.fetchone()['total']
                logger.info(f"Total messages in database: {total}")
            
            return messages
            
    except mysql.connector.Error as e:
        logger.error(f"Database fetch error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()


def test_database_connection():
    """Test database connectivity and basic operations."""
    print("🔧 Testing database connection...")
    
    try:
        # Test connection
        conn = get_connection()
        print("✅ Database connection successful!")
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL version: {version[0]}")
            
            # Test if messages table exists
            cursor.execute("SHOW TABLES LIKE 'messages'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ 'messages' table found!")
                
                # Show table structure
                cursor.execute("DESCRIBE messages")
                columns = cursor.fetchall()
                print("📋 Table structure:")
                for col in columns:
                    print(f"   - {col[0]} ({col[1]})")
            else:
                print("❌ 'messages' table not found!")
                return False
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def create_messages_table_if_not_exists():
    """Create the messages table if it doesn't exist (based on your schema)."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                msg_type VARCHAR(50) DEFAULT 'text',
                date DATETIME NOT NULL,
                date_unixtime INT NOT NULL,
                sender_name VARCHAR(255) NOT NULL,
                sender_id VARCHAR(255) NOT NULL,
                text TEXT NOT NULL,
                INDEX idx_date (date),
                INDEX idx_sender_id (sender_id),
                INDEX idx_date_sender (date, sender_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_table_query)
            conn.commit()
            print("✅ Messages table created or verified successfully!")
            
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    print("🚀 Butler Bot Database Manager")
    print("=" * 40)
    
    # Test database connection first
    if not test_database_connection():
        print("❌ Database connection failed. Please check your configuration.")
        exit(1)
    
    # Ensure table exists
    try:
        create_messages_table_if_not_exists()
    except Exception as e:
        print(f"❌ Failed to create/verify table: {e}")
        exit(1)
    
    # Insert a test message
    try:
        print("\n📝 Inserting test message...")
        insert_message_to_db(
            title="ButlerBot",
            content="Good morning, sir. This is a test message from your butler.",
            source="test_chat_123",
            msg_type="text"
        )
        print("✅ Test message inserted successfully!")
        
        # Fetch messages to verify
        print("\n📖 Fetching messages from test source...")
        messages = fetch_messages_between(
            "2020-01-01 00:00:00", 
            "2030-01-01 00:00:00", 
            "test_chat_123"
        )
        
        print(f"📋 Found {len(messages)} messages:")
        for msg in messages:
            print(f"   - [{msg['date']}] {msg['sender_name']}: {msg['content']}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()