import os
import logging
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from ultralytics import YOLO
import torch

# Set up logging
Path('scripts/logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename='scripts/logs/yolo_enrichment.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')
db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT')
}

# Initialize YOLOv8 model
model = YOLO('yolov8n.pt')  # Pre-trained YOLOv8 nano model

def create_classifications_table(conn):
    """Create the raw.image_classifications table if it doesn't exist."""
    create_table_query = """
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE TABLE IF NOT EXISTS raw.image_classifications (
        classification_id SERIAL PRIMARY KEY,
        message_id BIGINT,
        image_file VARCHAR,
        object_class VARCHAR,
        confidence FLOAT,
        load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (message_id) REFERENCES raw.telegram_messages(message_id)
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()
        logger.info("Ensured raw.image_classifications table exists")
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        conn.rollback()

def process_image(image_path, message_id, conn):
    """Process an image with YOLOv8 and store classifications."""
    try:
        # Run YOLOv8 inference
        results = model(image_path)
        detections = results[0].boxes  # Get bounding boxes

        with conn.cursor() as cur:
            for box in detections:
                cls_id = int(box.cls)  # Class ID
                object_class = model.names[cls_id]  # Class name (e.g., 'bottle', 'pill')
                confidence = float(box.conf)  # Confidence score

                # Map COCO classes to medical categories (simplified)
                medical_class = map_coco_to_medical(object_class)

                cur.execute("""
                    INSERT INTO raw.image_classifications (
                        message_id, image_file, object_class, confidence
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    message_id,
                    str(image_path),
                    medical_class,
                    confidence
                ))
            conn.commit()
        logger.info(f"Processed {image_path}: {len(detections)} objects detected")
    except Exception as e:
        logger.error(f"Error processing {image_path}: {str(e)}")
        conn.rollback()

def map_coco_to_medical(coco_class):
    """Map COCO classes to medical categories."""
    class_map = {
        'bottle': 'cream',  # Assume bottles are creams
        'pill': 'pill',     # Hypothetical; adjust based on model
        'syringe': 'syringe',
        'cup': 'bottle',    # Could be a container
    }
    return class_map.get(coco_class, 'unknown')

def main():
    """Process images with YOLOv8 and store classifications."""
    conn = psycopg2.connect(**db_params)
    try:
        create_classifications_table(conn)

        # Query images from raw.telegram_messages
        with conn.cursor() as cur:
            cur.execute("SELECT message_id, image_file FROM raw.telegram_messages WHERE has_image = TRUE")
            images = cur.fetchall()

        for message_id, image_file in images:
            image_path = Path(image_file)
            if image_path.exists():
                process_image(image_path, message_id, conn)
            else:
                logger.warning(f"Image not found: {image_path}")

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
