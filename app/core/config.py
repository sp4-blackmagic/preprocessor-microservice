from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
from dataclasses import dataclass

class PreprocessorVersion(Enum):
    PROD = 1  # Actual implementation
    MOCK = 2  # Mock implementation
    STUB = 3  # Stub implementation

class Settings(BaseSettings):
    APP_NAME: str = "Data Preprocessor Microservice"
    API_STR: str = "/preprocessor/api"
    CAMERA_TYPE: str = "VIS"
    PREPROCESSOR_VERSION: PreprocessorVersion = PreprocessorVersion.PROD 

    # For loading from .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()