from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional

from app.core.mongodb import MongoDBManager
from app.models.user_models import UserInfoResponse, UserCreateRequest, UserUpdateRequest
from app.utils.auth_utils import generate_api_key

router = APIRouter(prefix="/users", tags=["users"])


# ==================== Dependency ====================

def get_db(request: Request) -> MongoDBManager:
    """Get MongoDB connection from app state."""
    if not hasattr(request.app, 'db_manager') or request.app.db_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    return request.app.db_manager


# ==================== User Management Endpoints ====================

@router.post("/create", response_model=UserInfoResponse)
async def create_user(
    request: UserCreateRequest,
    db: MongoDBManager = Depends(get_db)
):
    """Create a new user."""
    try:
        # Check if user already exists
        existing_user = db.find_one("users", {"user_id": request.user_id})
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Create user document
        user_data = {
            "user_id": request.user_id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "username": request.username,
            "photo_url": request.photo_url,
            "api_key": generate_api_key(),
            "auto_exchange": request.auto_exchange
        }
        
        # Insert user
        user_id = db.insert_one("user", user_data)
        
        # Retrieve created user
        created_user = db.find_one("user", {"_id": user_id})
        
        return UserInfoResponse(
            user_id=created_user["user_id"],
            auto_exchange=created_user["auto_exchange"],
            first_name=created_user["first_name"],
            last_name=created_user["last_name"],
            username=created_user["username"],
            photo_url=created_user["photo_url"],
            api_key=created_user["api_key"],
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/{user_id}", response_model=UserInfoResponse)
async def get_user(
    user_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Get user by ID."""
    try:
        user = db.find_one("user", {"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserInfoResponse(
            user_id=user["user_id"],
            auto_exchange=user["auto_exchange"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            username=user["username"],
            photo_url=user["photo_url"],
            api_key=user["api_key"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")


@router.put("/{user_id}", response_model=UserInfoResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: MongoDBManager = Depends(get_db)
):
    """Update user settings."""
    try:
        # Check if user exists
        existing_user = db.find_one("user", {"user_id": user_id})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update data
        update_data = {"$set": {}}
        
        if request.auto_exchange is not None:
            update_data["$set"]["auto_exchange"] = request.auto_exchange
        
        if not update_data["$set"]:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update user
        result = db.update_one("user", {"user_id": user_id}, update_data)
        
        if result["modified_count"] == 0:
            raise HTTPException(status_code=400, detail="No changes made")
        
        # Return updated user
        updated_user = db.find_one("user", {"user_id": user_id})
        
        return UserInfoResponse(
            user_id=updated_user["user_id"],
            first_name=updated_user["first_name"],
            last_name=updated_user["last_name"],
            username=updated_user["username"],
            photo_url=updated_user["photo_url"],
            api_key=updated_user["api_key"],
            auto_exchange=updated_user["auto_exchange"],
            created_at=updated_user["created_at"],
            updated_at=updated_user["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Delete a user."""
    try:
        deleted_count = db.delete_one("user", {"user_id": user_id})
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User {user_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


@router.get("/")
async def list_users(
    limit: int = 50,
    skip: int = 0,
    auto_exchange: Optional[bool] = None,
    db: MongoDBManager = Depends(get_db)
):
    """List users with optional filtering."""
    try:
        # Build filter
        filter_dict = {}
        if auto_exchange is not None:
            filter_dict["auto_exchange"] = auto_exchange
        
        # Get users
        users = db.find_many(
            "user",
            filter_dict=filter_dict,
            sort=("created_at", -1),
            limit=limit,
            skip=skip
        )
        
        total_count = db.count_documents("user", filter_dict)
        
        return {
            "users": users,
            "total_count": total_count,
            "limit": limit,
            "skip": skip,
            "filters": {"auto_exchange": auto_exchange} if auto_exchange is not None else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")


# ==================== Auto-Exchange Management ====================

@router.post("/{user_id}/auto-exchange/enable")
async def enable_auto_exchange(
    user_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Enable auto-exchange for a user."""
    try:
        result = db.update_one(
            "user",
            {"user_id": user_id},
            {"$set": {"auto_exchange": True}},
            upsert=True
        )
        
        return {
            "user_id": user_id,
            "auto_exchange": True,
            "message": "Auto-exchange enabled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enabling auto-exchange: {str(e)}")


@router.post("/{user_id}/auto-exchange/disable")
async def disable_auto_exchange(
    user_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Disable auto-exchange for a user."""
    try:
        result = db.update_one(
            "user",
            {"user_id": user_id},
            {"$set": {"auto_exchange": False}},
            upsert=True
        )
        
        return {
            "user_id": user_id,
            "auto_exchange": False,
            "message": "Auto-exchange disabled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disabling auto-exchange: {str(e)}")


@router.get("/{user_id}/auto-exchange/status")
async def get_auto_exchange_status(
    user_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Get auto-exchange status for a user."""
    try:
        user = db.find_one("user", {"user_id": user_id})
        
        if not user:
            # Return default status for non-existent users
            return {
                "user_id": user_id,
                "auto_exchange": False,
                "exists": False
            }
        
        return {
            "user_id": user_id,
            "auto_exchange": user.get("auto_exchange", False),
            "exists": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting auto-exchange status: {str(e)}")