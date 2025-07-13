import os
import json
import logging
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# ------------------------------
# Set up logging
# ------------------------------
Path('scripts/logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename='scripts/logs/loading.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT')
}

# ------------------------------
# Create table with PRIMARY KEY
# ------------------------------
def create_raw_table(conn):
    """Create the raw messages table if it doesn't exist, with a PRIMARY KEY on message_id."""
    create_table_query = """
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        message_id BIGINT PRIMARY KEY,
        channel VARCHAR,
        scrape_date DATE,
        message_date TIMESTAMP,
        sender_id BIGINT,
        text TEXT,
        has_image BOOLEAN,
        image_file VARCHAR,
        message_length INTEGER,
        load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()
        logger.info("Ensured raw.telegram_messages table exists with PRIMARY KEY")
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        conn.rollback()

# ------------------------------
# Load JSON -> PostgreSQL safely
# ------------------------------
def load_json_to_postgres(json_file, conn):
    """Load a JSON file into the raw.telegram_messages table, skip duplicates."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)

        inserted = 0
        skipped = 0

        with conn.cursor() as cur:
            for msg in messages:
                message_length = len(msg['text'] or '')
                cur.execute("""
                    INSERT INTO raw.telegram_messages (
                        message_id, channel, scrape_date, message_date, sender_id,
                        text, has_image, image_file, message_length
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (message_id) DO NOTHING
                """, (
                    msg['message_id'],
                    msg['channel'],
                    msg['scrape_date'],
                    msg['message_date'],
                    msg['sender_id'],
                    msg['text'] or '',
                    msg['has_image'],
                    msg['image_file'],
                    message_length
                ))
                if cur.rowcount == 1:
                    inserted += 1
                else:
                    skipped += 1

            conn.commit()
        logger.info(f"Loaded {inserted} new, skipped {skipped} duplicates from {json_file}")
    except Exception as e:
        logger.error(f"Error loading {json_file}: {str(e)}")
        conn.rollback()

# ------------------------------
# Run Loader
# ------------------------------
def main():
    """Load all JSON files from the data lake into PostgreSQL."""
    data_dir = Path('data/raw/telegram_messages')
    conn = psycopg2.connect(**db_params)

    try:
        create_raw_table(conn)
        for json_file in data_dir.glob('*/*/*.json'):
            load_json_to_postgres(json_file, conn)
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
