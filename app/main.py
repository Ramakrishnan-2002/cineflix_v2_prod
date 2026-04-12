from fastapi import FastAPI
from .databases.database import init_db 
from contextlib import asynccontextmanager
from .routers import users,auth,reviews
from .middlewares.idempotency import init_redis, close_redis
from .middlewares.logger import get_logger

logger=get_logger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan: Initializing database and Redis")
    await init_db() 
    await init_redis()
    logger.info("Application lifespan initialization complete")
    yield
    await close_redis()
    logger.info("Application lifespan shutdown complete: Redis closed")


app=FastAPI(title="My Cineflix Application",tags=["health"],lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"} 

app.include_router(users.router)
app.include_router(auth.router)
# app.include_router(reviews.router)