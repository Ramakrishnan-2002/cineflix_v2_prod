from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI
from .logger import get_logger

logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

def apply_rate_limit(app: FastAPI, rate: str = "100/hour"):
    try:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        for route in app.routes:
            if hasattr(route, "endpoint"):
                route.endpoint = limiter.limit(rate)(route.endpoint)
        logger.info(f"Rate limiting applied to application with rate: {rate}")
        return app
    except Exception as e:
        logger.error(f"Error applying rate limit: {e}")
        raise