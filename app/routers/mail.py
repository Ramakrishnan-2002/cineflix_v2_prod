from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi.responses import RedirectResponse
from ..middlewares.logger import get_logger
from ..utilities.config import settings
from ..schemas.mail_schemas import ForgotEmail, ResetPassword
from ..middlewares.rate_limiter import limiter
from ..databases.models import User
from ..services.email_service import email_service
from ..configs.security import get_password_hash


router = APIRouter(prefix="/password", tags=["forgot-password"])
logger = get_logger(__name__)
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


@router.post("/forgot-password")
@limiter.limit("5/minute")
async def send_password_reset_mail(request : Request,email: ForgotEmail,background_tasks: BackgroundTasks):
    user = await User.find_one(User.email == email.email)
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    try:
        token = serializer.dumps(user.email, salt="password-reset-salt")
        email_service.send_password_reset_email(background_tasks=background_tasks, email=user.email, token=token, name=user.name)
        logger.info(f"Password reset email sent to: {email.email}")
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.exception(f"Error sending password reset email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error sending password reset email")
    

@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request : Request,data: ResetPassword):
    try:
        email= serializer.loads(data.token, salt="password-reset-salt", max_age=3600)
        user = await User.find_one(User.email == email)
        if not user:
            logger.warning(f"Password reset attempted with invalid token for email: {email}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.password = get_password_hash(data.new_password)
        await user.save()
        logger.info(f"Password reset successful for email: {email}")
        return {"message": "Password reset successful"}
    except (BadSignature,SignatureExpired):
        logger.warning(f"Invalid or expired token for password reset: {data.token}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    except Exception as e:
        logger.exception(f"Error resetting password: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error resetting password")
    

@router.get("/logout")
async def redirect_to_login():
    redirect_response= RedirectResponse(url="/docs",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response 