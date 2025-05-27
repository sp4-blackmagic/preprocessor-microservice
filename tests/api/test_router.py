from app.schemas.data_models import PreprocessingParameters
from app.schemas.exceptions import InvalidFileFormatError
from app.util.csv_utils import read_csv, generate_headers
import pytest

# ====================
# Creating Dummy Input
# ====================
@pytest.fixture
def raw_file():
    # Dummy raw file for testing
    content = b'\x01\x02\x03\x04' * 100
    return ("dummy.raw", content, "application/octet-stream")

@pytest.fixture
def bin_file():
    # Dummy bin file for testing
    content = b'\x05\x06\x07\x08' * 100
    return ("dummy.bin", content, "application/octet-stream")

@pytest.fixture
def hdr_file():
    # Dummy hdr file for testing
    content = b'ENVI\naqcuisition time = 2025-04-29T15:28:01,406332Z\nband names = {470nm, 600nm, 750nm, 900nm }\nbands=4\nfile type = ENVI Standard'
    return ("dummy.hdr", content, "application/octet-stream")

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
