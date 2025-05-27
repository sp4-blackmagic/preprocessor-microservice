from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.schemas.data_models import PreprocessingParameters, get_preprocessing_params
from app.schemas.exceptions import PreprocessingError
from app.util.validation import basic_file_validation
from typing import Optional
import os
import time

router = APIRouter()

STUB_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "example_data", "extracted_features.csv"
)

@router.post("/preprocess", response_class=FileResponse)
async def preprocess_data_stub(
    params: PreprocessingParameters = Depends(get_preprocessing_params), 
    hdr_file: Optional[UploadFile] = File(None), 
    cube_file: Optional[UploadFile] = File(None)
):
    """
    Stub endpoint: Always returns a prepared CSV file.

    Parameters
    ----------
    params: PreprocessingParameters
        Configuration for customizing the output
    hdrFile: UploadFile
        Header file of the data cube to be processed
    cubeFile: UploadFile
        The actual binary data of the data cube to be processed
    """
    try:
        basic_file_validation(hdr_file=hdr_file, cube_file=cube_file)
    except PreprocessingError as e:
        raise e  # re-raising the exception since its already formatted


    if not os.path.exists(STUB_CSV_PATH):
        raise HTTPException(
            status_code=500, 
            detail="STUB CSV file not found."
        )
    
    return FileResponse(
        path=STUB_CSV_PATH,
        media_type='text/csv',
        filename="processed_data.csv" 
    )
