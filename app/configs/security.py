from passlib.context import CryptContext
from ..utilities.config import settings
from typing import Optional
from datetime import datetime, timedelta,timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..databases.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_data:Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_data:
        expire = datetime.now(timezone.utc) + expires_data
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/auth/login")
async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception= HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = await User.find_one(User.email == email)
        if not user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        return user
    except jwt.PyJWTError:
        raise credentials_exception