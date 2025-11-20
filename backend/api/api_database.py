"""
Database configuration for FastAPI REST API.
Connects to the same Neon PostgreSQL database as the voice agent.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import agent-python modules
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=backend_dir / "api" / ".env.local")

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create async engine with Neon-optimized settings
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Session factory for creating async sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Note: We don't need to import Base here since we're using models from agent-python
# The models already have their Base defined in agent-python/database.py

async def get_db():
    """Dependency for getting database sessions in FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

logger.info("FastAPI database engine created - connected to Neon PostgreSQL")
