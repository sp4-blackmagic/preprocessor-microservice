from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, Response
import httpx
import os
from typing import Optional
from app.util.validation import basic_file_validation
from app.schemas.data_models import PreprocessingParameters, get_preprocessing_params
from app.schemas.exceptions import PreprocessingError
from app.core.preprocessor import preprocess
import tempfile

router = APIRouter()

@router.post("/preprocess")
async def preprocess_data(
    params: PreprocessingParameters = Depends(get_preprocessing_params), 
    hdr_file: Optional[UploadFile] = File(None), 
    cube_file: Optional[UploadFile] = File(None)
):
    """
    The main function hosting the logic to the actual preprocessing endpoint.
    Takes in a header file and a binary/raw of a data cube and calls the 
    preprocess function on them, the results of which are later returned
    in a .csv formatted text response

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
    
    if params.storage_endpoint == "":
        raise HTTPException(
            status_code=400,
            detail = f"Error: No storage endpoint provided"
        )
    
    try: 
        preprocessed_dataframe = await preprocess(hdr_file=hdr_file, cube_file=cube_file, params=params)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            # can't really clean up this link through os.unlink so leaving
            # it as is, probably don't have to do it either way since using `with``
            csv_file_path = temp_csv.name
            preprocessed_dataframe.to_csv(csv_file_path, index=False)

            # Send the file to storage        
            filename = hdr_file.filename.split(".")[0].lower()
            with open(csv_file_path, "rb") as f:
                files = {
                    "csv": (filename+".csv", f, "text/csv")
                }

                async with httpx.AsyncClient() as client:
                    print(f"Sending POST request to: {params.storage_endpoint} with file: {csv_file_path}")
                    response = await client.post(params.storage_endpoint, files=files, timeout=120.0)
                    body = response.json()
                    if response.status_code == 200:
                        print(f"File upload successful! Response body {body}")
                        return {
                            "uid": body["uid"],
                            "message": "Image preprocessed and data saved successfully"
                        }
                    else: 
                        raise HTTPException(
                            status_code=500,
                            detail=f"An error occured during saving the preprocessed data"
                        )
                       
    except Exception as e:
        raise HTTPException(
            status_code=500,   
            detail = f"Error: {e}"
        )