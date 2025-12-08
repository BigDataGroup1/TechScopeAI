"""
Database configuration helper for TechScopeAI.

Defaults to Cloud SQL connection. Local connection only when explicitly requested.
"""

import os
import logging
from urllib.parse import quote_plus
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables

logger = logging.getLogger(__name__)


def get_database_url(use_local: bool = False, database_url: Optional[str] = None) -> str:
    """
    Get PostgreSQL database connection URL.
    
    Priority order:
    1. Explicit database_url parameter
    2. DATABASE_URL environment variable
    3. Cloud SQL (via CLOUD_SQL_PASSWORD) - DEFAULT
    4. Local PostgreSQL (only if use_local=True)
    
    Args:
        use_local: If True, use local PostgreSQL (localhost:5432). 
                   If False (default), use Cloud SQL.
        database_url: Explicit database URL to use (overrides everything)
    
    Returns:
        PostgreSQL connection URL string
    
    Raises:
        ValueError: If Cloud SQL password is not found and use_local=False
    """
    # Priority 1: Explicit database_url parameter
    if database_url:
        logger.info(f"Using explicit database URL: {database_url.split('@')[-1] if '@' in database_url else 'provided'}")
        return database_url
    
    # Priority 2: DATABASE_URL environment variable
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        logger.info(f"Using DATABASE_URL from environment: {env_url.split('@')[-1] if '@' in env_url else 'provided'}")
        return env_url
    
    # Priority 3: Cloud SQL (default)
    if not use_local:
        cloud_password = os.getenv("CLOUD_SQL_PASSWORD")
        if cloud_password:
            # URL-encode password to handle special characters
            password_encoded = quote_plus(cloud_password)
            # Get optional Cloud SQL connection parameters
            cloud_host = os.getenv("CLOUD_SQL_HOST", "localhost")
            cloud_port = os.getenv("CLOUD_SQL_PORT", "5433")
            cloud_db = os.getenv("CLOUD_SQL_DB", "techscope")
            cloud_user = os.getenv("CLOUD_SQL_USER", "postgres")
            
            # Default Cloud SQL connection via proxy (localhost:5433)
            # For production Cloud Run, use: postgresql://postgres:password@/techscope?host=/cloudsql/PROJECT:REGION:INSTANCE
            cloud_url = f"postgresql://{cloud_user}:{password_encoded}@{cloud_host}:{cloud_port}/{cloud_db}"
            logger.info(f"Using Cloud SQL connection: {cloud_host}:{cloud_port}/{cloud_db}")
            return cloud_url
        else:
            # CLOUD_SQL_PASSWORD not found - this is an error since Cloud SQL is the default
            logger.error("CLOUD_SQL_PASSWORD not found in environment variables.")
            logger.error("Set CLOUD_SQL_PASSWORD environment variable or use use_local=True for local PostgreSQL.")
            raise ValueError(
                "CLOUD_SQL_PASSWORD not found. Cloud SQL is the default. "
                "Set CLOUD_SQL_PASSWORD in your .env file or environment, "
                "or use use_local=True to use local PostgreSQL."
            )
    
    # Priority 4: Local PostgreSQL (only if use_local=True)
    if use_local:
        local_password = os.getenv("LOCAL_POSTGRES_PASSWORD", "postgres")
        local_host = os.getenv("LOCAL_POSTGRES_HOST", "localhost")
        local_port = os.getenv("LOCAL_POSTGRES_PORT", "5432")
        local_db = os.getenv("LOCAL_POSTGRES_DB", "techscope")
        local_user = os.getenv("LOCAL_POSTGRES_USER", "postgres")
        
        local_url = f"postgresql://{local_user}:{local_password}@{local_host}:{local_port}/{local_db}"
        logger.info(f"Using LOCAL PostgreSQL connection: {local_host}:{local_port}/{local_db}")
        return local_url
    
    # If we get here, no valid configuration found
    raise ValueError(
        "No database configuration found. Set one of:\n"
        "  - DATABASE_URL environment variable\n"
        "  - CLOUD_SQL_PASSWORD environment variable (for Cloud SQL)\n"
        "  - use_local=True parameter (for local PostgreSQL)\n"
        "  - database_url parameter (explicit URL)"
    )

