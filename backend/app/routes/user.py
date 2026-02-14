from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.models.all_models import User
from app.schemas.all_schemas import UserResponse, UserUpdate
from app.dependencies.auth_dependency import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    user: User = Depends(get_current_user),
):
    """
    Get the current authenticated user's profile.
    """
    return user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_in: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current authenticated user's profile.
    """
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.address is not None:
        user.address = user_in.address
    if user_in.phone_number is not None:
        user.phone_number = user_in.phone_number
        
    await db.commit()
    await db.refresh(user)
    return user
