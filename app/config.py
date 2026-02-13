"""Application configuration management.

This module handles loading and validating environment variables and
application settings using Pydantic for type safety and validation.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings are loaded from environment variables or .env file.
    Uses Pydantic for automatic validation and type conversion.
    """
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/timetable_db",
        description="PostgreSQL connection URL for production"
    )
    database_url_dev: str = Field(
        default="sqlite:///./timetable_dev.db",
        description="SQLite connection URL for development"
    )
    
    # Security
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for session encryption (min 32 chars)"
    )
    jwt_secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token signing (min 32 chars)"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    jwt_expiration_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="JWT token expiration time (1-168 hours)"
    )
    
    # Application
    app_name: str = Field(
        default="Automated Timetable Scheduling System",
        description="Application name"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Server bind address"
    )
    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Server port (1024-65535)"
    )
    environment: str = Field(
        default="development",
        description="Deployment environment"
    )
    
    @field_validator("secret_key", "jwt_secret_key")
    @classmethod
    def validate_secret_keys(cls, v: str) -> str:
        """Validate secret keys are not default/example values."""
        if "change" in v.lower() or "example" in v.lower():
            raise ValueError(
                "Secret keys must be changed from example values. "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        return v
    
    @property
    def db_url(self) -> str:
        """Get appropriate database URL based on environment."""
        if self.environment == "production":
            return self.database_url
        return self.database_url_dev
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance.
    
    Settings are loaded once and cached for application lifetime.
    """
    return Settings()
