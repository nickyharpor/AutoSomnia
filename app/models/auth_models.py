from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelegramAuthData(BaseModel):
    """Telegram authentication data from Login Widget."""
    id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    username: Optional[str] = Field(None, description="Telegram username")
    photo_url: Optional[str] = Field(None, description="User's profile photo URL")
    auth_date: int = Field(..., description="Unix timestamp of authentication")
    hash: str = Field(..., description="HMAC-SHA-256 hash for verification")


class TokenResponse(BaseModel):
    """JWT token response."""
    token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")


class UserInfo(BaseModel):
    """User information."""
    id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    username: Optional[str] = Field(None, description="Telegram username")
    photo_url: Optional[str] = Field(None, description="User's profile photo URL")


class UserDocument(BaseModel):
    """User document stored in database."""
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: str
    last_login: str
    auto_exchange: bool = False
