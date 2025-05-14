from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.data_models import PreprocessingInput # Use if mock needs to validate input
import os

router = APIRouter()

MOCK_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data_mocks", "extracted_features.csv"
)

@router.post("/preprocess", response_class=FileResponse)
async def preprocess_data_mock(
    # input_data: PreprocessingInput # Optional: if your mock should still validate the input structure
):
    """
    Mock endpoint: Always returns a prepared CSV file.
    """
    if not os.path.exists(MOCK_CSV_PATH):
        raise HTTPException(status_code=500, detail="Mock CSV file not found.")
    
    return FileResponse(
        path=MOCK_CSV_PATH,
        media_type='text/csv',
        filename="processed_data_mock.csv" # Suggested filename for download
    )

# You can add more mock endpoints if needed