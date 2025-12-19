from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Parallel Online Judge API"
    API_V1_STR: str = "/api/v1"
    
    # ==========================================
    # Database Settings (PostgreSQL)
    # ==========================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # ==========================================
    # Redis Settings (Message Queue)
    # ==========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    REDIS_URL: Optional[str] = None

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

    def model_post_init(self, __context):
        if self.SQLALCHEMY_DATABASE_URI is None:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        if self.REDIS_URL is None:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

settings = Settings()