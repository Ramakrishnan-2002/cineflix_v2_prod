from passlib.context import CryptContext
from ..utilities.config import settings
from typing import Optional
from datetime import datetime, timedelta,timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..databases.models import User
from ..middlewares.logger import get_logger

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    try:
        hash_result = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hash_result
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str):
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug("Password verification completed")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        raise


def create_access_token(data: dict, expires_data:Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        if expires_data:
            expire = datetime.now(timezone.utc) + expires_data
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.info(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/auth/login")
async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception= HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token validation failed: No email in token payload")
            raise credentials_exception
        user = await User.find_one(User.email == email)
        if not user:
            logger.warning(f"Token validation failed: User not found for email: {email}")
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        logger.info(f"User authenticated successfully: {email}")
        return user
    except jwt.PyJWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise credentials_exception