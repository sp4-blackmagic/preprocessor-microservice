from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

class PreprocessorVersion(Enum):
    PROD = 1,  # Actual implementation
    MOCK = 2,  # Mock implementation
    STUB = 3  # Stub implementation


class Settings(BaseSettings):
    APP_NAME: str = "Data Preprocessor Microservice"
    API_STR: str = "/preprocessor/api"
    PREPROCESSOR_VERSION: PreprocessorVersion = PreprocessorVersion.STUB 

    # For loading from .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()