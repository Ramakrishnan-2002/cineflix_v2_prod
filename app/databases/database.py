from .models import User,Review
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from ..utilities.config import settings
from ..middlewares.logger import get_logger

logger=get_logger(__name__)

if not hasattr(AsyncIOMotorClient, "append_metadata"):
    AsyncIOMotorClient.append_metadata = lambda self, *args, **kwargs: None

async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGO_URL)
        await init_beanie(database=client.get_default_database(), document_models=[User,Review])
        logger.info("Database initialized successfully with Beanie and Motor")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e 