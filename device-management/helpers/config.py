"""
Configuration module for Device Management Microservice.
Loads environment variables and sets up database connections.
"""

from typing import Final
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

# Environment variables with defaults
USER_DB: Final[str] = os.getenv('USER_DB', 'admin')
PASSWORD_DB: Final[str] = os.getenv('PASSWORD_DB', '1234')
NAME_DB: Final[str] = os.getenv('NAME_DB', 'db_device_management')
SERVER_DB: Final[str] = os.getenv('SERVER_DB', 'localhost')

# Redis configuration
REDIS_HOST: Final[str] = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT: Final[int] = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB: Final[int] = int(os.getenv('REDIS_DB', '0'))

# JWT configuration (must match Signing service)
JWT_SECRET_KEY: Final[str] = os.getenv('JWT_SECRET_KEY', '$argon2id$v=19$m=65536,t=3,p=4$hT18aCPZ5AFxQ2ncYkRkWg$5UvBttA1brZmn6Bmf1T0NgKaYaqUzMV1pvWNxDp5pFc')
JWT_ALGORITHM: Final[str] = os.getenv('JWT_ALGORITHM', 'HS256')

# RabbitMQ configuration
RABBITMQ_HOST: Final[str] = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT: Final[int] = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER: Final[str] = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD: Final[str] = os.getenv('RABBITMQ_PASSWORD', 'guest')

# PostgreSQL connection URL
URL_DB: Final[str] = f'postgresql+psycopg2://{USER_DB}:{PASSWORD_DB}@{SERVER_DB}:5432/{NAME_DB}'

# SQLAlchemy setup
# Increased pool size and recycle time to prevent timeouts and stale connections
engine = create_engine(
    URL_DB, 
    pool_size=50,
    max_overflow=30,
    pool_recycle=1800,
    pool_pre_ping=True
)
LocalSession = sessionmaker(bind=engine)
Base = declarative_base()


def session_factory():
    """
    Dependency for FastAPI to get a database session.
    Yields the session and closes it after use.
    """
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()


# Logging setup
def setup_logger():
    """Configure logging for the application."""
    formater = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    os.makedirs('./logs', exist_ok=True)
    
    handler = logging.FileHandler('./logs/device_management.log')
    handler.setFormatter(formater)
    logger = logging.getLogger('device_management')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


logger = setup_logger()
