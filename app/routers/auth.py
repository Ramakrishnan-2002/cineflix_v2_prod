from fastapi import APIRouter, HTTPException, Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from ..databases.models import User
from ..configs import security

router=APIRouter(prefix="/auth",tags=["auth"])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user= await User.find_one(User.email==form_data.username)
    if not user or not security.verify_password(form_data.password,user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid email or password")
    access_token=security.create_access_token(data={"sub": user.email},expires_data=security.timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}