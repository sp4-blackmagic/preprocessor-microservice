from fastapi import HTTPException, status

class PreprocessingError(HTTPException):
    """Base exception for preprocessing errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class InvalidFileFormatError(PreprocessingError):
    """Raise when a non-ENVI header file is uploaded"""
    def __init__(self, detail: str = "Invalid file format. Only ENVI header files, and .bin/.raw data cube files are supported.",
                 status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class MissingMetadataError(PreprocessingError):
    """Raise when required metadata (like wavelengths) is missing from the header file"""
    def __init__(self, detail: str = "Missing essential metadata in HDR file (e.g., wavelengths). Cannot proceed with preprocessing.",
                 status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class DataProcessingError(PreprocessingError):
    """Raise for errors during the processing itself"""
    def __init__(self, detail: str = "Internal error occurred during data processing.",
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)

class BackgroundRemovalError(PreprocessingError):
    """Raises if background removal fails unexpectedly"""
    def __init__(self, detail: str = "Internal error occurred during background removal.",
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)