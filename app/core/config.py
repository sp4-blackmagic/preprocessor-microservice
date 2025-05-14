from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Data Preprocessor Microservice"
    API_V1_STR: str = "/api/v1"
    USE_MOCK_PREPROCESSOR: bool = True # Default to True for easy start

    # For loading from .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()