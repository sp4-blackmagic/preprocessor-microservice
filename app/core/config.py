from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Data Preprocessor Microservice"
    API_STR: str = "/preprocessor/api"
    USE_MOCK_PREPROCESSOR: bool = True 

    # For loading from .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()