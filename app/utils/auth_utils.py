import hashlib
import hmac
import time
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Configuration - these should be in environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_telegram_authentication(auth_data: dict, bot_token: str) -> bool:
    """
    Verify Telegram authentication data integrity using HMAC-SHA-256.
    
    This implements the verification algorithm specified by Telegram:
    https://core.telegram.org/widgets/login#checking-authorization
    
    Args:
        auth_data: Dictionary with Telegram auth data (including hash)
        bot_token: Your Telegram bot token
    
    Returns:
        bool: True if data is valid and signature matches
    
    Example:
        >>> data = {
        ...     "id": 123456789,
        ...     "first_name": "John",
        ...     "auth_date": 1699564800,
        ...     "hash": "abc123..."
        ... }
        >>> verify_telegram_authentication(data, "your_bot_token")
        True
    """
    # Extract and remove hash from data
    received_hash = auth_data.pop('hash', None)
    if not received_hash:
        return False
    
    # Create data check string (sorted key=value pairs separated by newlines)
    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items()) if v is not None]
    data_check_string = '\n'.join(data_check_arr)
    
    # Create secret key (SHA256 hash of bot token)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Calculate HMAC-SHA256
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare hashes using constant-time comparison to prevent timing attacks
    return hmac.compare_digest(calculated_hash, received_hash)


def check_auth_date(auth_date: int, max_age_seconds: int = 86400) -> bool:
    """
    Check if auth_date is not too old (prevents replay attacks).
    
    Args:
        auth_date: Unix timestamp from Telegram
        max_age_seconds: Maximum age in seconds (default: 24 hours)
    
    Returns:
        bool: True if auth_date is recent enough
    
    Example:
        >>> import time
        >>> current_time = int(time.time())
        >>> check_auth_date(current_time)
        True
        >>> check_auth_date(current_time - 90000)  # More than 24 hours ago
        False
    """
    current_time = int(time.time())
    age = current_time - auth_date
    return age <= max_age_seconds


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token (e.g., user_id, telegram_id)
        expires_delta: Token expiration time (optional)
    
    Returns:
        str: Encoded JWT token
    
    Example:
        >>> token_data = {"user_id": 123, "telegram_id": 456}
        >>> token = create_access_token(token_data)
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    
    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = verify_token(token)
        >>> print(payload['user_id'])
        123
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise credentials_exception
        
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        raise credentials_exception


def get_telegram_user_id_from_token(token: str) -> int:
    """
    Extract Telegram user ID from JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        int: Telegram user ID
    
    Raises:
        HTTPException: If token is invalid or doesn't contain telegram_id
    """
    payload = verify_token(token)
    telegram_id = payload.get("telegram_id")
    
    if telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload - missing telegram_id"
        )
    
    return telegram_id


def generate_api_key(length: int = 32, prefix: str = "") -> str:
    """
    Generate a random API key.
    
    Args:
        length: Length of the random part (default: 32 characters)
        prefix: Optional prefix for the API key (e.g., "sk_", "api_")
    
    Returns:
        str: Generated API key
    
    Example:
        >>> api_key = generate_api_key()
        >>> print(api_key)
        'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
        
        >>> api_key = generate_api_key(prefix="sk_")
        >>> print(api_key)
        'sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
    """
    import secrets
    
    # Generate random URL-safe string
    random_part = secrets.token_urlsafe(length)
    
    # Remove any padding characters and limit to specified length
    random_part = random_part.replace('-', '').replace('_', '')[:length]
    
    # Combine prefix with random part
    api_key = f"{prefix}{random_part}"
    
    return api_key
