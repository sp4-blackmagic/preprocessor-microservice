import pytest
import pytest_asyncio
from app.schemas.data_models import PreprocessingParameters
from app.core.preprocessor import preprocess

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
    content = b'DIMENSIONS=10,10,1\nDATATYPE=uint8\n'
    return ("dummy.hdr", content, "application/octet-stream")

@pytest.fixture
def params():
    return PreprocessingParameters()

@pytest.mark.asyncio
async def test_upload_wrong_hdr_format(hdr_file, bin_file, params):
    with pytest.raises(AttributeError):
        await preprocess(hdr_file=hdr_file, cube_file=bin_file, params=params)