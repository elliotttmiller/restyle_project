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
    Load environment variables from .env file if it exists, 
    otherwise log a message but don't treat it as an error in production.
    
    Returns:
        bool: True if .env was loaded, False otherwise
    """
    env_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / '.env'
    alt_env_path = Path('/') / '.env'  # Root path in Railway container
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"Loaded environment variables from {env_path}")
        return True
    elif alt_env_path.exists():
        load_dotenv(dotenv_path=alt_env_path)
        logger.info(f"Loaded environment variables from {alt_env_path}")
        return True
    else:
        # In production (Railway), env vars are set through the platform
        # so we don't need to log this as an error
        if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
            logger.info("Running in Railway production environment. Using platform environment variables.")
        else:
            logger.warning(f".env file not found at: {env_path} or {alt_env_path}")
        
        return False
