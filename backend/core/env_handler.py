"""
Environment variable handler to gracefully handle missing .env files in production.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_environment_variables():
    """
    Load environment variables from a .env file.
    Searches for the .env file in the current directory and the parent directory.
    """
    # Look for .env in the project root (one level up from `backend/core`)
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path_root = project_root / '.env'

    # Also check the conventional location relative to manage.py
    backend_root = Path(__file__).resolve().parent.parent
    dotenv_path_backend = backend_root / '.env'

    if dotenv_path_root.exists():
        load_dotenv(dotenv_path=dotenv_path_root)
        logger.info(f"✅ Loaded environment variables from: {dotenv_path_root}")
    elif dotenv_path_backend.exists():
        load_dotenv(dotenv_path=dotenv_path_backend)
        logger.info(f"✅ Loaded environment variables from: {dotenv_path_backend}")
    else:
        logger.warning(f".env file not found. Searched in {dotenv_path_root} and {dotenv_path_backend}.")
