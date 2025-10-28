from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""
    user_id: int = Field(..., description="Telegram user ID")
    auto_exchange: bool = Field(default=False, description="Auto-exchange enabled status")


class UserResponse(BaseModel):
    """Response model for user data."""
    user_id: int = Field(..., description="Telegram user ID")
    auto_exchange: bool = Field(..., description="Auto-exchange enabled status")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserUpdateRequest(BaseModel):
    """Request model for updating user settings."""
    auto_exchange: Optional[bool] = Field(None, description="Auto-exchange enabled status")
