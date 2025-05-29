from fastapi import UploadFile, File
from typing import Optional
from app.schemas.exceptions import InvalidFileFormatError


def basic_file_validation(
    hdr_file: Optional[UploadFile] = File(None), 
    cube_file: Optional[UploadFile] = File(None)
) -> bool:
    """
    Returns true if provided files meet system
    requirements, raises a corresponding exception
    otherwise
    """
    try:
        if cube_file is None:
            raise InvalidFileFormatError(detail="The data cube file is missing from the request data.")
        elif hdr_file is None:
            raise InvalidFileFormatError(detail="The request provided a data cube file bit is missing a corresponding header file.")
        else:
            # Basic file validation
            allowed_cube_extensions = [".raw", ".bin"]
            if not hasattr(hdr_file, "filename"):
                raise InvalidFileFormatError(detail="The provided hdr file is invalid - no attribute 'filename'")
            if not hasattr(cube_file, "filename"):
                raise InvalidFileFormatError(detail="The provided cube file is invalid - no attribute 'filename'")
            hdr_extension = "." + hdr_file.filename.split(".")[-1].lower()
            cube_extension = "." + cube_file.filename.split(".")[-1].lower()
            if hdr_extension != ".hdr":
                raise InvalidFileFormatError(detail="Invalid header file extension. Only '.hdr' extensions are supported.")
            if cube_extension not in allowed_cube_extensions:
                raise InvalidFileFormatError(detail="Invalid data cube file extension. Only '.raw' and '.bin' extensions are supported")
            if not hasattr(hdr_file, "file"):
                raise InvalidFileFormatError(detail="The provided hdr file is invalid - no attribute 'file'")
            if not hasattr(cube_file, "file"):
                raise InvalidFileFormatError(detail="The provided cube file is invalid - no attribute 'file'")
    except Exception as e:
        raise InvalidFileFormatError(detail=f"Error occurred while validating uploaded files. Exception: {e}")

    return True
