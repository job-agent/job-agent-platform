"""Database configuration."""

import os
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    model_config = {"env_prefix": "DB_"}

    url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "postgresql://localhost:5432/jobs"),
        description="PostgreSQL connection URL",
    )
    pool_size: int = Field(
        default=10,
        description="Database connection pool size",
    )
    max_overflow: int = Field(
        default=20,
        description="Maximum overflow connections",
    )
    echo: bool = Field(
        default=False,
        description="Enable SQL query logging",
    )


def get_database_config() -> DatabaseConfig:
    """
    Get database configuration from environment.

    Returns:
        DatabaseConfig instance
    """
    return DatabaseConfig()
