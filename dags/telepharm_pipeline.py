from dagster import job, op, ScheduleDefinition, get_dagster_logger
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()
logger = get_dagster_logger()

@op
def scrape_telegram_data(context):
    """Run Telegram scraping script."""
    logger.info("Starting Telegram scrape")
    try:
        result = subprocess.run(
            ["python", "scripts/scrape_telegram.py"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Scrape completed: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Scrape failed: {e.stderr}")
        raise

@op
def load_raw_to_postgres(context):
    """Load raw data to PostgreSQL."""
    logger.info("Starting data load to PostgreSQL")
    try:
        result = subprocess.run(
            ["python", "scripts/load_to_postgres.py"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Load completed: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Load failed: {e.stderr}")
        raise

@op
def run_yolo_enrichment(context):
    """Run YOLOv8 enrichment on images."""
    logger.info("Starting YOLOv8 enrichment")
    try:
        result = subprocess.run(
            ["python", "scripts/enrich_with_yolo.py"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Enrichment completed: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Enrichment failed: {e.stderr}")
        raise

@op
def run_dbt_transformations(context):
    """Run dbt transformations and tests."""
    logger.info("Starting dbt run")
    try:
        run_result = subprocess.run(
            ["make", "dbt-run"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"dbt run completed: {run_result.stdout}")

        test_result = subprocess.run(
            ["make", "dbt-test"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"dbt test completed: {test_result.stdout}")
        return run_result.stdout + test_result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"dbt failed: {e.stderr}")
        raise

@job
def telepharm_pipeline():
    """Define the TelePharm Insights pipeline."""
    scrape_output = scrape_telegram_data()
    load_output = load_raw_to_postgres(scrape_output)
    enrich_output = run_yolo_enrichment(load_output)
    run_dbt_transformations(enrich_output)

# Daily schedule at 08:00 UTC
telepharm_schedule = ScheduleDefinition(
    job=telepharm_pipeline,
    cron_schedule="0 8 * * *",
    execution_timezone="UTC"
)
