from app.schemas.data_models import PreprocessingParameters
from fastapi import UploadFile
import numpy as np
import pytest
import io

# ====================
# Creating Dummy Input
# ====================
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
        b"wavelengths = {470.0, 600.0, 750.0, 900.0}\n"
        b"wavelength units = Nanometers\n"
    )
    return UploadFile(
        filename="dummy.hdr",
        file=io.BytesIO(hdr_content)
    )

@pytest.fixture
def wrong_hdr_file():
    content = b'Some random content'
    file_obj = io.BytesIO(content)
    return UploadFile(
        filename="wrong.hdr",
        file=file_obj
)

@pytest.fixture
def params():
    return PreprocessingParameters()


# ================
# Test Definitions
# ================
def test_service_alive(client):
    """
    Test if the service was properly started
    """
    response = client.get("/")
    assert response.status_code == 200

def test_upload_and_preprocess_bin_success(client, hdr_file, bin_file):
    # Reset file pointers for each test
    hdr_file.file.seek(0)
    bin_file.file.seek(0)

    _files = {
        "hdr_file": (hdr_file.filename, hdr_file.file, "application/octet-stream"),
        "cube_file": (bin_file.filename, bin_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)

    # Check general response
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]

def test_upload_and_preprocess_raw_success(client, hdr_file, raw_file):
    hdr_file.file.seek(0)
    raw_file.file.seek(0)

    _files = {
        "hdr_file": (hdr_file.filename, hdr_file.file, "application/octet-stream"),
        "cube_file": (raw_file.filename, raw_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_no_input_failure(client):
    response = client.post("/preprocessor/api/preprocess")
    assert response.status_code == 400


def test_missing_cube_file_failure(client, hdr_file):
    _files = {
        "hdr_file": (hdr_file.filename, hdr_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)
    assert response.status_code == 400

def test_missing_hdr_file_failure(client, bin_file, raw_file):
    # Test with inputing only the binary file first
    _files = {
        "cube_file": (bin_file.filename, bin_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)
    assert response.status_code == 400

    # Test with input only the raw file also
    _files = {
        "cube_file": (raw_file.filename, raw_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)
    assert response.status_code == 400

def test_upload_wrong_hdr_bin_failure(client, wrong_hdr_file, bin_file):
    _files = {
        "hdr_file": (wrong_hdr_file.filename, wrong_hdr_file.file, "application/octet-stream"),
        "cube_file": (bin_file.filename, bin_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)
    print(response)
    # Check general response
    assert response.status_code == 400

def test_upload_wrong_hdr_raw_failure(client, wrong_hdr_file, raw_file):
    _files = {
        "hdr_file": (wrong_hdr_file.filename, wrong_hdr_file.file, "application/octet-stream"),
        "cube_file": (raw_file.filename, raw_file.file, "application/octet-stream")
    }

    response = client.post("/preprocessor/api/preprocess", files=_files)
    print(response)
    assert response.status_code == 400
