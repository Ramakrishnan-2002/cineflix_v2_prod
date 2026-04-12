from ..utilities.config import settings
import redis.asyncio as redis
from fastapi import HTTPException, Header, status
from .logger import get_logger

logger = get_logger(__name__)

redis_client=redis.from_url(settings.REDIS_URL, decode_responses=True)

async def init_redis():
    try:
        await redis_client.ping()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Redis: {e}")
        raise e

async def close_redis():
    await redis_client.close()
    logger.info("Redis closed successfully")

async def verify_idempotency_key(x_idempotency_key:str = Header(None)):
    if not x_idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Idempotency-Key header is required")
    try:
        exists = await redis_client.get(f"idempotency:{x_idempotency_key}")
        if exists:
            logger.warning(f"Duplicate request detected with idempotency key: {x_idempotency_key}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate request: Request already processed. Please wait a few minutes before retrying.")
        await redis_client.set(f"idempotency:{x_idempotency_key}", "processed", ex=3600)
        logger.info(f"Idempotency key verified: {x_idempotency_key}")
        return x_idempotency_key 
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying idempotency key: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error while verifying idempotency key")