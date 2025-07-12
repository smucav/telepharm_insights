import os
import json
import logging
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from dotenv import load_dotenv

# === Load .env ===
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# === Setup Directories ===
DATA_DIR = Path('data/raw/telegram_messages')
LOG_DIR = Path('scripts/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === Setup Logging ===
logging.basicConfig(
    filename=LOG_DIR / 'scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Channels ===
CHANNELS = [
    'Chemed123',
    'lobelia4cosmetics',
    'tikvahpharma'
]

async def scrape_channel(client, channel):
    """Scrape messages + images from a Telegram channel."""
    try:
        entity = await client.get_entity(channel)
        channel_name = entity.username or entity.title
        logger.info(f"Scraping channel: {channel_name}")

        # Create output dir: YYYY-MM-DD
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_dir = DATA_DIR / date_str / channel_name
        output_dir.mkdir(parents=True, exist_ok=True)

        messages_data = []
        async for message in client.iter_messages(entity, limit=50):
            msg_data = {
                'message_id': message.id,
                'channel': channel_name,
                'scrape_date': date_str,
                'message_date': message.date.isoformat(),
                'sender_id': message.sender_id,
                'text': message.text,
                'has_image': bool(message.photo),
                'image_file': None
            }

            if message.photo:
                image_path = output_dir / f"{channel_name}_{message.id}.jpg"
                await client.download_media(message.photo, image_path)
                msg_data['image_file'] = str(image_path)
                logger.info(f"Downloaded image: {image_path}")

            messages_data.append(msg_data)

        # Save messages to JSON
        output_file = output_dir / f"{channel_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(messages_data)} messages to {output_file}")

    except FloodWaitError as e:
        logger.error(f"Rate limit hit for {channel}: wait {e.seconds} seconds.")
    except Exception as e:
        logger.error(f"Error scraping {channel}: {str(e)}")


async def main():
    """Main orchestration."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    async with TelegramClient('telepharm_session', API_ID, API_HASH) as client:
        try:
            await client.start(phone=PHONE)
            logger.info("Telegram client started.")

            for channel in CHANNELS:
                await scrape_channel(client, channel)

        except SessionPasswordNeededError:
            logger.error("2FA is enabled: please handle password.")
        except Exception as e:
            logger.error(f"Client error: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
