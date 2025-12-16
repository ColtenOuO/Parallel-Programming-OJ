from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Parallel Online Judge API"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "poj_db"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SUPER_SECRET_KEY"
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()