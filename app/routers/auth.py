from fastapi import APIRouter, HTTPException, Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from ..databases.models import User
from ..configs import security
from ..middlewares.logger import get_logger

logger = get_logger(__name__)
router=APIRouter(prefix="/auth",tags=["auth"])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for email: {form_data.username}")
    try:
        user= await User.find_one(User.email==form_data.username)
        if not user or not security.verify_password(form_data.password,user.password):
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid email or password")
        access_token=security.create_access_token(data={"sub": user.email},expires_data=security.timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        logger.info(f"Login successful for email: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during login for email: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")