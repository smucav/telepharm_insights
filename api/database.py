import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT')
}

def get_db():
    """provide a database connection"""
    conn = psycopg2.connect(**db_params, options="-c search_path=raw_marts,raw_staging,public")
    try:
        yield conn
    finally:
        conn.close()
