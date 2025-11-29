import os
import logging
from fastapi import APIRouter, HTTPException, Depends, status, Request, Header
from typing import Optional

from app.models.auth_models import TelegramAuthData, TokenResponse
from app.utils.auth_utils import (
    verify_telegram_authentication,
    check_auth_date,
    create_access_token,
    get_telegram_user_id_from_token
)
from app.core.mongodb import MongoDBManager
from bot.config.bot_config import Config

# Load bot configuration
bot_config = Config()

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_db(request: Request) -> MongoDBManager:
    """Get MongoDB connection from app state."""
    if not hasattr(request.app, 'db_manager') or request.app.db_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    return request.app.db_manager


@router.post("/telegram", response_model=TokenResponse)
async def authenticate_telegram(
    auth_data: TelegramAuthData,
    db: MongoDBManager = Depends(get_db)
):
    """
    Authenticate user via Telegram Login Widget.
    
    This endpoint:
    1. Verifies the HMAC-SHA-256 hash of the data
    2. Checks that auth_date is recent (< 24 hours)
    3. Creates or updates user in database
    4. Generates JWT token
    5. Returns token and user info
    
    Args:
        auth_data: Telegram authentication data from widget
        db: Database connection
    
    Returns:
        TokenResponse with JWT token and user information
    
    Raises:
        HTTPException 401: If hash verification fails or data is expired
        HTTPException 500: If bot token is not configured
    
    Example:
        ```
        POST /auth/telegram
        {
            "id": 123456789,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "auth_date": 1699564800,
            "hash": "abc123..."
        }
        ```
    """
    # Get bot token from bot config
    bot_token = bot_config.BOT_TOKEN
    if not bot_token:
        logger.error("BOT_TOKEN not configured in bot config")
        raise HTTPException(
            status_code=500,
            detail="Telegram bot token not configured. Please set BOT_TOKEN in .env file."
        )
    
    # Convert to dict for verification
    data_dict = auth_data.model_dump()
    
    # Verify hash
    logger.info(f"Verifying Telegram authentication for user ID: {auth_data.id}")
    if not verify_telegram_authentication(data_dict.copy(), bot_token):
        logger.warning(f"Hash verification failed for user ID: {auth_data.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data - hash verification failed"
        )
    
    # Check auth_date (prevent replay attacks)
    if not check_auth_date(auth_data.auth_date, max_age_seconds=86400):
        logger.warning(f"Auth date expired for user ID: {auth_data.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication data expired (older than 24 hours)"
        )
    
    # Get or create user in database
    try:
        user = db.find_one("user", {"user_id": auth_data.id})
        
        if not user:
            # Create new user
            logger.info(f"Creating new user with Telegram ID: {auth_data.id}")
            user_data = {
                "user_id": auth_data.id,  # Use telegram_id as user_id for consistency
                "first_name": auth_data.first_name,
                "last_name": auth_data.last_name,
                "username": auth_data.username,
                "photo_url": auth_data.photo_url,
                "auto_exchange": False
            }
            db.insert_one("user", user_data)
            user = user_data
        else:
            # Update last login and user info
            logger.info(f"Updating existing user with Telegram ID: {auth_data.id}")
            update_data = {
                "first_name": auth_data.first_name,
                "last_name": auth_data.last_name,
                "username": auth_data.username,
                "photo_url": auth_data.photo_url
            }
            db.update_one(
                "user",
                {"user_id": auth_data.id},
                {"$set": update_data}
            )
            # Update user dict with new data
            user.update(update_data)
        
    except Exception as e:
        logger.error(f"Database error during user creation/update: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    
    # Create JWT token
    # TODO add datetime for expiry
    token_data = {
        "user_id": user.get("user_id", auth_data.id),
        "username": auth_data.username,
        "first_name": auth_data.first_name
    }
    
    try:
        access_token = create_access_token(token_data)
        logger.info(f"Successfully authenticated user: {auth_data.username or auth_data.first_name}")
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error creating access token"
        )
    
    return TokenResponse(
        token=access_token,
        token_type="bearer",
        user={
            "id": auth_data.id,
            "first_name": auth_data.first_name,
            "last_name": auth_data.last_name,
            "username": auth_data.username,
            "photo_url": auth_data.photo_url
        }
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    Note: Since we're using JWT tokens, logout is handled client-side
    by removing the token from storage. This endpoint exists for
    consistency and can be extended to implement token blacklisting
    if needed.
    
    Returns:
        Success message
    """
    logger.info("User logout requested")
    return {
        "message": "Logged out successfully",
        "detail": "Token should be removed from client storage"
    }


@router.get("/verify")
async def verify_token_endpoint(
    authorization: Optional[str] = Header(None),
    db: MongoDBManager = Depends(get_db)
):
    """
    Verify JWT token and return user data.
    
    This endpoint can be used to:
    - Check if a token is still valid
    - Get current user information
    - Refresh user data from database
    
    Args:
        authorization: Bearer token from Authorization header
        db: Database connection
    
    Returns:
        User information if token is valid
    
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 404: If user not found in database
    
    Example:
        ```
        GET /auth/verify
        Headers: Authorization: Bearer <token>
        ```
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token and get telegram_id
    try:
        telegram_id = get_telegram_user_id_from_token(token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )
    
    # Get user from database
    try:
        user = db.find_one("user", {"telegram_id": telegram_id})
        
        if not user:
            logger.warning(f"User not found for telegram_id: {telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.get("telegram_id"),
            "user_id": user.get("user_id"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "username": user.get("username"),
            "photo_url": user.get("photo_url"),
            "auto_exchange": user.get("auto_exchange", False),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error during user lookup: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )


@router.get("/me")
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: MongoDBManager = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Alias for /auth/verify endpoint with a more RESTful name.
    
    Args:
        authorization: Bearer token from Authorization header
        db: Database connection
    
    Returns:
        Current user information
    """
    return await verify_token_endpoint(authorization, db)


@router.get("/health")
async def auth_health_check():
    """
    Health check for authentication service.
    
    Returns:
        Service status and configuration info
    """
    bot_token_configured = bool(bot_config.BOT_TOKEN)
    jwt_secret_configured = bool(os.getenv("JWT_SECRET_KEY"))
    
    return {
        "status": "healthy",
        "service": "authentication",
        "telegram_bot_configured": bot_token_configured,
        "jwt_secret_configured": jwt_secret_configured,
        "endpoints": {
            "login": "/auth/telegram",
            "logout": "/auth/logout",
            "verify": "/auth/verify",
            "me": "/auth/me"
        }
    }
