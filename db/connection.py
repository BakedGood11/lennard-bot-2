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

def get_connection():
    """
    Establish connection to the MySQL database using environment variables.
    
    Returns:
        mysql.connector.connection: Database connection object
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "192.168.1.120"),
            user=os.getenv("DB_USER", "lennard"), 
            password=os.getenv("DB_PASS", "745311"),
            database=os.getenv("DB_NAME", "telegram"),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
        return connection
    except mysql.connector.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise


def insert_message_to_db(title, content, source, msg_type="text"):
    """
    Insert a message into the messages table.
    
    Args:
        title (str): Sender name (maps to sender_name)
        content (str): Message text (maps to text)
        source (str): Chat/sender ID (maps to sender_id)
        msg_type (str): Type of message (default: "text")
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Fixed query to match your actual table structure
            query = """
                INSERT INTO messages (msg_type, date, date_unixtime, sender_name, sender_id, text)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Get current time in both formats
            now = datetime.now(pytz.UTC)
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")
            date_unix = int(time.time())
            
            # Execute with correct parameter mapping
            cursor.execute(query, (
                msg_type,      # msg_type
                date_str,      # date  
                date_unix,     # date_unixtime
                title,         # sender_name
                source,        # sender_id (chat_id)
                content        # text
            ))
            
            conn.commit()
            logger.info(f"Message inserted successfully for {title}")
            
    except mysql.connector.Error as e:
        logger.error(f"Database insert error: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error during insert: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


def fetch_messages_between(start_dt, end_dt, source):
    """
    Fetch messages between specified time ranges for a specific source.
    
    Args:
        start_dt (str): Start datetime in 'YYYY-MM-DD HH:MM:SS' format
        end_dt (str): End datetime in 'YYYY-MM-DD HH:MM:SS' format  
        source (str): Chat/sender ID to filter by
        
    Returns:
        list: List of dictionaries containing message data
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cursor:
            # Fixed query to use correct table and column names
            query = """
                SELECT id, msg_type, date, date_unixtime, sender_name, sender_id, text as content
                FROM messages 
                WHERE date BETWEEN %s AND %s AND sender_id = %s
                ORDER BY date ASC
            """
            
            cursor.execute(query, (start_dt, end_dt, source))
            results = cursor.fetchall()
            
            logger.info(f"Fetched {len(results)} messages between {start_dt} and {end_dt}")
            return results
            
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