from fastapi import APIRouter, HTTPException, status, Depends ,Request
from ..schemas.user_schemas import UserCreate,UserResponse
from ..databases.models import User
from ..configs import security
from ..configs.security import get_current_user
from ..middlewares.logger import get_logger
from ..middlewares.rate_limiter import limiter
from ..middlewares.idempotency import verify_idempotency_key

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create",status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_user(request:Request,user:UserCreate):
    try:
        logger.info("Create user request received for email: %s", user.email)
        existing_user = await User.find_one(User.email == user.email)
        if existing_user:
            logger.warning("User creation failed - email already exists: %s", user.email)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        password_hash = security.get_password_hash(user.password)
        new_user = User(name=user.name, email=user.email, password=password_hash)
        await new_user.save()
        logger.info("User created successfully: %s", user.email)
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error creating user: %s", user.email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/all", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
@limiter.limit("20/minute")
async def get_all_users(request: Request):
    try:
        logger.info("Fetch all users request received")
        users = await User.find_all().to_list()
        logger.info("Returning %d users", len(users))
        return users
    except Exception as e:
        logger.exception("Unexpected error fetching all users")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/delete/{user_email}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def delete_user(request: Request, user_email: str, current_user: User = Depends(get_current_user)):
    try:
        logger.info("Delete user request received for email: %s by user: %s", user_email, getattr(current_user, "email", "unknown"))
        user = await User.find_one(User.email == user_email)
        if not user:
            logger.warning("Delete failed - user not found: %s", user_email)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await user.delete()
        logger.info("User deleted successfully: %s", user_email)
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error deleting user: %s", user_email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/update/{user_email}", status_code=status.HTTP_200_OK, response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user(request: Request, user_email: str, user: UserCreate, current_user: User = Depends(get_current_user)):
    try:
        logger.info("Update user request received for target email: %s by user: %s", user_email, getattr(current_user, "email", "unknown"))
        existing_user = await User.find_one(User.email == user_email)
        if not existing_user:
            logger.warning("Update failed - user not found: %s", user_email)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        existing_user.name = user.name
        existing_user.email = user.email
        existing_user.password = security.get_password_hash(user.password)
        await existing_user.save()
        logger.info("User updated successfully: %s", user.email)
        return existing_user
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error updating user: %s", user_email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/update-name/{user_email}", status_code=status.HTTP_200_OK, response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user_name(request: Request, user_email: str, new_name: str, current_user: User = Depends(get_current_user)):
    try:
        logger.info("Update user name request received for email: %s, new name: %s, by user: %s", user_email, new_name, getattr(current_user, "email", "unknown"))
        existing_user = await User.find_one(User.email == user_email)
        if not existing_user:
            logger.warning("Update name failed - user not found: %s", user_email)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        existing_user.name = new_name
        await existing_user.save()
        logger.info("User name updated successfully for email: %s", user_email)
        return existing_user
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error updating user name: %s", user_email)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))