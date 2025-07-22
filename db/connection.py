import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime 
import pytz  

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database="lennard_db"
    )

# Insert message into the `documents` table
def insert_message_to_db(title, content, source, language="en"):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO documents (title, content, language, source, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            # Use UTC now
            utc_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(query, (title, content, language, source, utc_now))
            conn.commit()
    finally:
        conn.close()

# Fetch messages between time ranges
def fetch_messages_between(start_dt, end_dt, source):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
                SELECT title, content, created_at FROM documents
                WHERE created_at BETWEEN %s AND %s AND source = %s
                ORDER BY created_at ASC
            """
            cursor.execute(query, (start_dt, end_dt, source))
            return cursor.fetchall()
    finally:
        conn.close()
        
if __name__ == "__main__":
    # Insert a test row
    try:
        print("Inserting a test row...")
        insert_message_to_db(
            title="Test Title",
            content="This is a test message.",
            source="test_source",
            language="en"
        )
        print("✅ Inserted test row.")

        # Fetch and print rows from the test source
        print("Fetching rows from 'test_source'...")
        rows = fetch_messages_between("2000-01-01 00:00:00", "2100-01-01 00:00:00", "test_source")
        for row in rows:
            print(row)
    except Exception as e:
        print("❌ Error during DB test:", e)