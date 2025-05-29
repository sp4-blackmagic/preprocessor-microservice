import pytest
import io
import numpy as np
import pandas as pd
from app.schemas.data_models import PreprocessingParameters
from app.schemas.exceptions import InvalidFileFormatError, BackgroundRemovalError, MissingMetadataError, DataProcessingError
from app.core.preprocessor import preprocess
from fastapi import UploadFile

# ====================
# Creating Dummy Input
# ====================
@pytest.fixture
def invalid_raw_file():
    # Dummy raw file for testing
    content = b'\x01\x02\x03\x04' * 100
    return ("invalid.raw", content, "application/octet-stream")

@pytest.fixture
def invalid_bin_file():
    # Dummy bin file for testing
    content = b'\x05\x06\x07\x08' * 100
    return ("invalid.bin", content, "application/octet-stream")

@pytest.fixture
def invalid_hdr_file():
    # Dummy hdr file for testing
    content = b'DIMENSIONS=10,10,1\nDATATYPE=uint8\n'
    return ("invalid.hdr", content, "application/octet-stream")

@pytest.fixture
def params():
    return PreprocessingParameters()

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
def background_bin_file() -> UploadFile:
    content = np.zeros(shape=(10, 10, 4), dtype=np.float32).tobytes()
    file_obj = io.BytesIO(content)
    return UploadFile(
        filename="background.bin",
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

@pytest.fixture
def wrong_bands_hdr_file() -> UploadFile:
    hdr_content = (
        b"ENVI\n"
        b"description = {Dummy ENVI Header}\n"
        b"samples = 10\n"
        b"lines = 10\n"
        b"bands = 6\n"  # Mismatched amount of bands
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

@pytest.fixture
def wrong_wavelength_values_hdr_file() -> UploadFile:
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
        b"wavelength = {banana, mogging, baby gronk, $#*^@}\n" # Wavelengths are not number values
        b"wavelength units = Nanometers\n"
    )
    return UploadFile(
        filename="dummy.hdr",
        file=io.BytesIO(hdr_content)
    )

@pytest.fixture
def wrong_wavelength_amount_hdr_file() -> UploadFile:
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
        b"wavelength = {470.0, 600.0, 900.0}\n" # 4 bands but only 3 corresponding wavelengths
        b"wavelength units = Nanometers\n"
    )
    return UploadFile(
        filename="dummy.hdr",
        file=io.BytesIO(hdr_content)
    )


# ================
# Test Definitions
# ================

@pytest.mark.asyncio
async def test_upload_wrong_hdr_format(invalid_hdr_file, invalid_bin_file, params):
    with pytest.raises(InvalidFileFormatError):
        await preprocess(hdr_file=invalid_hdr_file, cube_file=invalid_bin_file, params=params)

@pytest.mark.asyncio
async def test_upload_invalid_cube_file_bin(hdr_file, invalid_bin_file, params):
    with pytest.raises(InvalidFileFormatError):
        await preprocess(hdr_file=hdr_file, cube_file=invalid_bin_file, params=params)

@pytest.mark.asyncio
async def test_upload_invalid_cube_file_raw(hdr_file, invalid_raw_file, params):
    with pytest.raises(InvalidFileFormatError):
        await preprocess(hdr_file=hdr_file, cube_file=invalid_raw_file, params=params)

@pytest.mark.asyncio
async def test_upload_bin_success(hdr_file, bin_file, params):
    result = await preprocess(hdr_file, bin_file, params)
    assert isinstance(result, pd.DataFrame)

@pytest.mark.asyncio
async def test_upload_raw_success(hdr_file, raw_file, params):
    result = await preprocess(hdr_file, raw_file, params)
    assert isinstance(result, pd.DataFrame)

@pytest.mark.asyncio
async def test_no_foreground_cube_file_exception(hdr_file, background_bin_file, params):
    params.remove_background = True
    with pytest.raises(BackgroundRemovalError):
        await preprocess(hdr_file=hdr_file, cube_file=background_bin_file, params=params)

@pytest.mark.asyncio
async def test_wrong_band_hdr_data_exception(wrong_bands_hdr_file, bin_file, params):
    with pytest.raises(DataProcessingError):
        await preprocess(hdr_file=wrong_bands_hdr_file, cube_file=bin_file, params=params)

@pytest.mark.asyncio
async def test_wrong_wavelength_values_hdr_exception(wrong_wavelength_values_hdr_file, bin_file, params):
    with pytest.raises(MissingMetadataError):
        await preprocess(hdr_file=wrong_wavelength_values_hdr_file, cube_file=bin_file, params=params)


@pytest.mark.asyncio
async def test_wrong_wavelength_amount_hdr_exception(wrong_wavelength_amount_hdr_file, bin_file, params):
    with pytest.raises(MissingMetadataError):
        await preprocess(hdr_file=wrong_wavelength_amount_hdr_file, cube_file=bin_file, params=params)