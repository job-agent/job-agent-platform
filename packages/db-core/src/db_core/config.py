"""Database configuration.

This module provides database configuration management:
- DatabaseConfig: Pydantic model for database settings
- get_database_config: Function to create config from environment
"""

import os

from pydantic import BaseModel, Field, StrictBool


class DatabaseConfig(BaseModel):
    """Database configuration settings.

    Attributes:
        url: PostgreSQL connection URL (required, from DATABASE_URL env var)
        pool_size: Database connection pool size (default: 10)
        max_overflow: Maximum overflow connections (default: 20)
        echo: Enable SQL query logging (default: False)
    """

    url: str = Field(
        description="PostgreSQL connection URL",
    )
    pool_size: int = Field(
        default=10,
        description="Database connection pool size",
        ge=1,
    )
    max_overflow: int = Field(
        default=20,
        description="Maximum overflow connections",
        ge=0,
    )
    echo: StrictBool = Field(
        default=False,
        description="Enable SQL query logging",
    )

    def __init__(self, url: str | None = None, **data):
        """Initialize DatabaseConfig, reading URL from environment if not provided."""
        if url is None:
            url = os.getenv("DATABASE_URL")
            if url is None:
                raise ValueError(
                    "DATABASE_URL environment variable is required. "
                    "Set DATABASE_URL or provide url parameter."
                )
        super().__init__(url=url, **data)


def get_database_config() -> DatabaseConfig:
    """Get database configuration from environment.

    Returns:
        DatabaseConfig instance populated from environment variables

    Raises:
        ValueError: If DATABASE_URL environment variable is not set
    """
    return DatabaseConfig()
