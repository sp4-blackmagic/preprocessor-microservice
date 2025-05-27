from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
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
    

    try: 
        preprocessed_dataframe = await preprocess(hdr_file=hdr_file, cube_file=cube_file, params=params)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            # can't really clean up this link through os.unlink so leaving
            # it as is, probably don't have to do it either way since using `with``
            csv_file_path = temp_csv.name
            preprocessed_dataframe.to_csv(csv_file_path, index=False)

        return FileResponse(
            path=csv_file_path,
            media_type="text/csv",
            filename="processed_reflectance_data.csv"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,   
            detail = f"Error: {e}"
        )