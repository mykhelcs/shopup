from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.models.all_models import User
from app.schemas.all_schemas import UserResponse
from app.dependencies.auth_dependency import get_current_user

router = APIRouter()

@router.post("/verify", response_model=UserResponse)
async def verify_token(
    user: User = Depends(get_current_user),
):
    """
    Verify Firebase token and return user info.
    This endpoint is called by the Flutter app after Firebase authentication.
    """
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: User = Depends(get_current_user),
):
    """
    Register endpoint - called after Firebase registration.
    The user is auto-created in get_current_user if it doesn't exist.
    This endpoint just returns the user info.
    """
    return user
