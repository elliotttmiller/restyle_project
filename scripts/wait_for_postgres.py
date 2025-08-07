import os
import time
import psycopg2
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_postgres(db_url: str, timeout: int = 120, delay: int = 5):
    """
    Waits for the PostgreSQL database to be available.

    Args:
        db_url (str): The database connection URL.
        timeout (int): The maximum time to wait in seconds.
        delay (int): The delay between retries in seconds.
    """
    start_time = time.time()
    logger.info("Waiting for PostgreSQL database to become available...")

    while time.time() - start_time < timeout:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            logger.info("✅ PostgreSQL database is available.")
            return True
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not yet available: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            time.sleep(delay)

    logger.error(f"❌ Timed out after {timeout} seconds waiting for the database.")
    return False

if __name__ == "__main__":
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set. Cannot wait for database.")
        exit(1)

    if not wait_for_postgres(database_url):
        exit(1)
