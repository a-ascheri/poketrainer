from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"
    CORS_ORIGIN_REGEX: str = r"^https://.*\.ngrok-free\.app$"

    class Config:
        env_file = ".env"


settings = Settings()
