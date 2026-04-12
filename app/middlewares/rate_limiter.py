from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

limiter = Limiter(key_func=get_remote_address)

def apply_rate_limit(app: FastAPI, rate: str = "100/hour"):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    for route in app.routes:
        if hasattr(route, "endpoint"):
            route.endpoint = limiter.limit(rate)(route.endpoint)
    return app