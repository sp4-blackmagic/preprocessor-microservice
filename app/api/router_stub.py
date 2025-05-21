from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.schemas.data_models import PreprocessingParameters
from typing import Optional
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
    if params_json is None:
        params = PreprocessingParameters()
    else:
        try:
            params = PreprocessingParameters.model_validate_json(params_json)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters for the request: {e}"
            )

    if hdr_file is None and cube_file is None:
        # Load data from storage service
        time.sleep(0.1)
    elif cube_file is None:
        raise HTTPException(
            status_code=400,
            detail="The request provided a header file but is missing a corresponding data cube file"
        )
    elif hdr_file is None:
        raise HTTPException(
            status_code=400,
            detail="The request provided a data cube file bit is missing a corresponding header file"
        )
    else:
        # Basic file validation
        allowed_cube_extensions = [".raw", ".bin"]
        hdr_extension = "." + hdr_file.filename.split(".")[-1].lower()
        cube_extension = "." + cube_file.filename.split(".")[-1].lower()
        if hdr_extension != ".hdr":
            raise HTTPException(
                status_code=400,
                detail="Invalid data cube header file type. Only .hdr extensions are supported."
            )
        if cube_extension not in allowed_cube_extensions:
            raise HTTPException(
                status_code=400,
                detail="Invalid data cube file type. Only .raw and .bin extensions are supported"
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
