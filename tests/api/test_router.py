from app.schemas.data_models import PreprocessingParameters
from app.util.csv_utils import read_csv, generate_headers
from fastapi import UploadFile
import pytest
import io

# ====================
# Creating Dummy Input
# ====================
@pytest.fixture
def raw_file() -> UploadFile:
    # Dummy raw file for testing
    content = b'\x01\x02\x03\x04' * 100
    return UploadFile(
        filename="dummy.raw",
        file=io.BytesIO(content)
    )

@pytest.fixture
def bin_file() -> UploadFile:
    # Dummy bin file for testing
    content = b'\x05\x06\x07\x08' * 100
    return UploadFile(
        filename="dummy.bin",
        file=io.BytesIO(content)
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
    return ("dummy.hdr", content, "application/octet-stream")

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

def test_upload_and_preprocess_bin_success(client, params, hdr_file, bin_file):
    _files = {
        "hdr_file": hdr_file,
        "cube_file": bin_file
    }

    _data = {
        "params_json": params.model_dump_json()
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)

    # Check general response
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]

    # Check response format
    csv_reader = read_csv(response.content, "utf-8")
    csv_response_header = next(csv_reader)
    expected_headers = generate_headers(params.extraction_methods, params.bands, params.extra_features)
    assert csv_response_header == expected_headers

def test_upload_and_preprocess_raw_success(client, params, hdr_file, raw_file):
    _files = {
        "hdr_file": hdr_file,
        "cube_file": raw_file
    }

    _data = {
        "params_json": params.model_dump_json()
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_no_input_failure(client):
    response = client.post("/preprocessor/api/preprocess")
    assert response.status_code == 400


def test_missing_cube_file_failure(client, params, hdr_file):
    _files = {
        "hdr_file": hdr_file
    }

    _data = {
        "params_json": params.model_dump_json()
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)
    assert response.status_code == 400

def test_missing_hdr_file_failure(client, params, bin_file, raw_file):
    # Test with inputing only the binary file first
    _files = {
        "cube_file": bin_file
    }

    _data = {
        "params_json": params.model_dump_json()
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)
    assert response.status_code == 400

    # Test with input only the raw file also
    _files = {
        "cube_file": raw_file
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)
    assert response.status_code == 400

def test_upload_wrong_hdr_bin_failure(client, params, wrong_hdr_file, bin_file):
    _files = {
        "hdr_file": wrong_hdr_file,
        "cube_file": bin_file
    }

    _data = {
        "params_json": params.model_dump_json()
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)
    print(response)
    # Check general response
    assert response.status_code == 400

def test_upload_wrong_hdr_raw_failure(client, params, wrong_hdr_file, raw_file):
    _files = {
        "hdr_file": wrong_hdr_file,
        "cube_file": raw_file
    }

    _data = {
        "params_json": params.model_dump_json()
    }

    response = client.post("/preprocessor/api/preprocess", files=_files, data=_data)
    print(response)
    assert response.status_code == 400
