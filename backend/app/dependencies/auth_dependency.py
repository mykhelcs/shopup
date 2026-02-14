from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials, initialize_app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.connection import get_db
from app.models.all_models import User, UserRole
from app.core.config import get_settings
import os
import logging

settings = get_settings()
security = HTTPBearer()

# Initialize Firebase (Ensure you have the credentials file or use environment variables)
# For now, we will wrap this safe initialization
try:
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        initialize_app(cred)
    else:
        # Fallback for dev/test without credentials - MOCKED env
        # In production this should fail
        logging.warning("Firebase credentials not found. Auth will fail unless mocked.")
except Exception as e:
    logging.warning(f"Firebase init skipped or failed: {e}")

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        # Verify Firebase Token with real verification
        decoded_token = auth.verify_id_token(token.credentials)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not found in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user exists in DB
        result = await db.execute(select(User).where(User.firebase_uid == uid))
        user = result.scalars().first()

        if not user:
            # Auto-create user on first login
            user = User(firebase_uid=uid, email=email, role=UserRole.CUSTOMER)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        return user

    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin(
    user: User = Depends(get_current_user)
) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return user

async def get_optional_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
