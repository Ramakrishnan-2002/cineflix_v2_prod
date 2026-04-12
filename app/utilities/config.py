from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    SECRET_KEY : str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str
    class Config:
        env_file = ".env"

settings = Settings() 