from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.schemas.data_models import PreprocessingParameters
from typing import Optional
from app.util.verification import VerificationResult, verify_hdr_and_cube_input
import os
import time

router = APIRouter()

STUB_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "example_data", "extracted_features.csv"
)

@router.post("/preprocess", response_class=FileResponse)
async def preprocess_data_stub(
    params_json: Optional[str] = Form(None), 
    hdr_file: Optional[UploadFile] = File(None), 
    cube_file: Optional[UploadFile] = File(None)
):
    """
    Stub endpoint: Always returns a prepared CSV file.
    Parameters
    ----------
    params: PreprocessingParameters
        Configuration for customizing the output. If its
        not provided, the default values are used
    hdrFile: UploadFile
        Header file of the data cube to be processed. If this and
        the cube file are not provided, its considered that it should
        load them from the storage service
    cubeFile: UploadFile
        The actual binary data of the data cube to be processed. If this and
        the header file are not provided, its considered that it should
        load them from the storage service
    """
    # Params validation
    params: PreprocessingParameters = PreprocessingParameters()
    if params_json is not None:
        try:
            params = PreprocessingParameters.model_validate_json(params_json)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters for the request: {e}"
            )

    # Basic file validation
    if not hdr_file and not cube_file:
        # TODO: Load the most recent files from storage service
        raise HTTPException(
            status_code=501,
            detail="Loading files from the storage component is not implemented yet."
        )
    else:
        result: VerificationResult = verify_hdr_and_cube_input(hdr_file, cube_file)
        if result.status_code != 200:
            raise HTTPException(
                status_code = result.status_code,
                detail = result.message
            )


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
