from fastapi import UploadFile
from app.schemas.exceptions import InvalidFileFormatError
from app.util.validation import basic_file_validation
import pytest
import numpy as np
import io

@pytest.fixture
def wrong_raw_file():
    content = b'\x01\x02\x03\x04' * 100
    return ("wrong.raw", content, "application/octet-stream")

@pytest.fixture
def wrong_bin_file():
    content = b'\x01\x02\x03\x04' * 100
    return ("wrong.bin", content, "application/octet-stream")

@pytest.fixture
def wrong_hdr_file():
    content = b'DIMENSIONS=10,10,1\nDATATYPE=uint8\n'
    return ("wrong.hdr", content, "application/octet-stream")

@pytest.fixture
def raw_file() -> UploadFile:
    # Dummy raw file for testing
    # should be tiny, only 400 B
    content = np.random.rand(10, 10, 4).astype(np.float32).tobytes()
    file_obj = io.BytesIO(content)
    return UploadFile(
        filename="dummy.raw",
        file=file_obj
    )

@pytest.fixture
def bin_file() -> UploadFile:
    # Dummy bin file for testing
    content = np.random.rand(10, 10, 4).astype(np.float32).tobytes()
    file_obj = io.BytesIO(content)
    return UploadFile(
        filename="dummy.bin",
        file=file_obj
    )

@pytest.fixture
def hdr_file() -> UploadFile:
    # Dummy hdr file for testing
    hdr_content = (
        b"ENVI\n"
        b"description = {Dummy ENVI Header}\n"
        b"samples = 10\n"
        b"lines = 10\n"
        b"bands = 4\n"
        b"header offset = 0\n"
        b"data type = 4\n"
        b"interleave = bsq\n"
        b"byte order = 0\n"
        b"wavelength = {470.0, 600.0, 750.0, 900.0}\n"
        b"wavelength units = Nanometers\n"
    )
    return UploadFile(
        filename="dummy.hdr",
        file=io.BytesIO(hdr_content)
    )

def test_no_files_provided():
    with pytest.raises(InvalidFileFormatError, match="The data cube file is missing from the request data."):
        result = basic_file_validation(None, None)

def test_no_hdr_file(bin_file):
    with pytest.raises(InvalidFileFormatError, match="The request provided a data cube file bit is missing a corresponding header file."):
        result = basic_file_validation(hdr_file=None, cube_file=bin_file)

def test_wrong_header_file_extension(raw_file):
    with pytest.raises(InvalidFileFormatError, match="Invalid header file extension. Only '.hdr' extensions are supported."):
        result = basic_file_validation(hdr_file=raw_file, cube_file=raw_file)

def test_wrong_cube_file_extension(hdr_file):
    with pytest.raises(InvalidFileFormatError, match="Invalid data cube file extension. Only '.raw' and '.bin' extensions are supported"):
        result = basic_file_validation(hdr_file=hdr_file, cube_file=hdr_file)

def test_invalid_header_file(wrong_hdr_file, bin_file):
    with pytest.raises(InvalidFileFormatError, match="The provided hdr file is invalid - no attribute 'filename'"):
        result = basic_file_validation(hdr_file=wrong_hdr_file, cube_file=bin_file)

def test_invalid_cube_file_bin(hdr_file, wrong_bin_file):
    with pytest.raises(InvalidFileFormatError, match="The provided cube file is invalid - no attribute 'filename'"):
        result = basic_file_validation(hdr_file=hdr_file, cube_file=wrong_bin_file)

def test_invalid_cube_file_raw(hdr_file, wrong_raw_file):
    with pytest.raises(InvalidFileFormatError, match="The provided cube file is invalid - no attribute 'filename'"):
        result = basic_file_validation(hdr_file=hdr_file, cube_file=wrong_raw_file)