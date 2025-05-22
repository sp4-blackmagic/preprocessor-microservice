from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from dataclasses import dataclass

@dataclass
class VerificationResult:
    status_code: int
    message: str

def verify_hdr_and_cube_input(
    hdr_file: Optional[UploadFile] = File(None), 
    cube_file: Optional[UploadFile] = File(None)
):
    """
    Returns a VarificationResult object indicating
    whether the passed hdr and cube files meet the
    system requirements
    """
    if cube_file is None:
        return VerificationResult(
            status_code = 400,
            message = "The request provided a header file but is missing a corresponding data cube file"
        )
    elif hdr_file is None:
        return VerificationResult(
            status_code=400,
            message="The request provided a data cube file bit is missing a corresponding header file"
        )
    else:
        # Basic file validation
        allowed_cube_extensions = [".raw", ".bin"]
        hdr_extension = "." + hdr_file.filename.split(".")[-1].lower()
        cube_extension = "." + cube_file.filename.split(".")[-1].lower()
        if hdr_extension != ".hdr":
            return VerificationResult(
                status_code=400,
                message="Invalid data cube header file type. Only .hdr extensions are supported."
            )
        if cube_extension not in allowed_cube_extensions:
            return VerificationResult(
                status_code=400,
                message="Invalid data cube file type. Only .raw and .bin extensions are supported"
            )
        
    return VerificationResult (
        status_code = 200,
        message = ""
    )
