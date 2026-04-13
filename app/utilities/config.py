from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    SECRET_KEY : str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    YOUTUBE_API_KEY:str
    YOUTUBE_API_URL:str
    class Config:
        env_file = ".env"

settings = Settings() 