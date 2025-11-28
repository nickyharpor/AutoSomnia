from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""
    user_id: int = Field(..., description="Telegram user ID")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    username: Optional[str] = Field(None, description="Telegram username")
    photo_url: Optional[str] = Field(None, description="Telegram photo URL")
    auto_exchange: bool = Field(default=False, description="Auto-exchange enabled status")


class UserInfoResponse(BaseModel):
    """Response model for user data."""
    user_id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    username: str = Field(..., description="Telegram username")
    photo_url: str = Field(..., description="Telegram photo URL")
    auto_exchange: bool = Field(..., description="Auto-exchange enabled status")
    api_key: str = Field(..., description="User's API key")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserUpdateRequest(BaseModel):
    """Request model for updating user settings."""
    auto_exchange: Optional[bool] = Field(None, description="Auto-exchange enabled status")
