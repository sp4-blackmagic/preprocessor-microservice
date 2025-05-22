from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
from app.util.verification import verify_hdr_and_cube_input, VerificationResult
from app.schemas.data_models import PreprocessingParameters
import io

router = APIRouter()


# Add `response_model` if returning structured JSON
@router.post("/preprocess")
async def preprocess_data(
    params_json: Optional[str] = Form(None), 
    hdr_file: Optional[UploadFile] = File(None), 
    cube_file: Optional[UploadFile] = File(None)
):
    """
    The main function hosting the logic to the actual preprocessing endpoint.
    Takes in a header file and a binary of a data cube and processes it, 
    by extracting data from each pixel for each wavelengt band using
    - Statistical Features
    - Average Spectrum
    - Spectral Derivatives (Savitzky-Golay)
    - Continuum Removal
    - FFT Features
    Returns the preprocessing results as a csv file or saves them
    to the running instance of the storage microservice

    Parameters
    ----------
    params: PreprocessingParameters
        Configuration for customizing the output
    hdrFile: UploadFile
        Header file of the data cube to be processed
    cubeFile: UploadFile
        The actual binary data of the data cube to be processed
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

    # --- TODO: Implement preprocessing logic ---

    # For now just raising an error because not implemented
    raise HTTPException(
        status_code=501,
        detail="Real preprocessor not yet implemented."
    )


# Example of an endpoint that might accept a file upload for preprocessing
@router.post("/preprocess-file-upload")
async def preprocess_uploaded_file_real(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):  # Basic validation
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV supported."
        )

    # contents = await file.read()
    # Process the contents (which will be bytes, decode if necessary)
    # For example, decode to string and then process as CSV
    # csv_data_string = contents.decode('utf-8')
    # ... your processing logic ...

    processed_csv_string = """
    processed_header,processed_value\n
    uploaded_and_done,123
    """

    s_buf = io.StringIO()
    s_buf.write(processed_csv_string)
    s_buf.seek(0)
    bytes_buf = io.BytesIO(s_buf.getvalue().encode())

    return StreamingResponse(
        bytes_buf,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"""attachment;
            filename=processed_{file.filename}"""
        }
    )
