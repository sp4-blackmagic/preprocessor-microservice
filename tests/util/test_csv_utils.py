import pytest
import numpy as np
import pandas as pd
from app.util.csv_utils import read_csv, create_feature_row
from app.schemas.data_models import ExtractionMethods, PreprocessingParameters


def test_read_csv_basic():
    """Test reading a simple CSV string."""
    csv_data = b"header1,header2\nvalue1,value2\n1,2"
    reader = read_csv(csv_data, "utf-8")
    
    # Read all rows and convert to list for easy assertion
    rows = list(reader)
    assert rows == [["header1", "header2"], ["value1", "value2"], ["1", "2"]]

def test_read_csv_empty():
    """Test reading an empty CSV string."""
    csv_data = b""
    reader = read_csv(csv_data, "utf-8")
    rows = list(reader)
    assert rows == []

def test_read_csv_different_delimiter():
    """Test reading a CSV with a different delimiter (though csv.reader defaults to comma)."""
    csv_data = b"a;b\nc;d"
    reader = read_csv(csv_data, "utf-8")
    rows = list(reader)
    # csv.reader by default expects comma. This tests its default behavior.
    assert rows == [["a;b"], ["c;d"]] 

def test_read_csv_non_utf8_encoding():
    """Test reading a CSV with a different valid encoding."""
    csv_data = "col1,col2\neuro,test".encode("latin-1")
    reader = read_csv(csv_data, "latin-1")
    rows = list(reader)
    assert rows == [["col1", "col2"], ["euro", "test"]]

def test_read_csv_invalid_encoding():
    """Test reading a CSV with an invalid encoding (should raise UnicodeDecodeError)."""
    csv_data = b"\x80" # Invalid byte for utf-8
    with pytest.raises(UnicodeDecodeError):
        read_csv(csv_data, "utf-8")


# --- Tests for create_feature_row ---

def test_create_feature_row_no_extras_single_feature():
    """Test creating a feature row with no extra features and one spectral feature."""
    features_dict = {ExtractionMethods.AVG_SPECTRUM: np.array([0.1, 0.2, 0.3])}
    params = PreprocessingParameters(extra_features=False, target_bands=3)
    
    df = create_feature_row(features_dict, params)
    
    expected_columns = [
        f"{ExtractionMethods.AVG_SPECTRUM.value}_b0",
        f"{ExtractionMethods.AVG_SPECTRUM.value}_b1",
        f"{ExtractionMethods.AVG_SPECTRUM.value}_b2"
    ]
    expected_data = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
    
    pd.testing.assert_frame_equal(df, pd.DataFrame(expected_data, columns=expected_columns))
    assert df.dtypes.iloc[0] == np.float32

def test_create_feature_row_with_extras_multiple_features():
    """Test creating a feature row with extra features and multiple spectral features."""
    features_dict = {
        ExtractionMethods.AVG_SPECTRUM: np.array([0.1, 0.2]),
        ExtractionMethods.FIRST_DERIV_AVG_SPECTRUM: np.array([0.01, -0.01])
    }
    params = PreprocessingParameters(extra_features=True, target_bands=2)

    # Sort dictionary items by enum value for consistent order
    sorted_features_dict = dict(sorted(features_dict.items(), key=lambda item: item[0].value))

    df = create_feature_row(sorted_features_dict, params)

    expected_extra_cols = [
        "record_json_id", "original_file_ref", "fruit", "day", "side", 
        "camera_type", "ripeness_state", "ripeness_state_fine", "firmness", 
        "init_weight", "storage_days"
    ]
    expected_spectral_cols = [
        "avg_spectrum_b0", "avg_spectrum_b1",
        "deriv1_avg_spectrum_b0", "deriv1_avg_spectrum_b1"
    ]
    expected_columns = expected_extra_cols + expected_spectral_cols
    
    expected_data = np.array([
        [np.nan] * len(expected_extra_cols) + [0.1, 0.2, 0.01, -0.01]
    ], dtype=np.float32)

    pd.testing.assert_frame_equal(df, pd.DataFrame(expected_data, columns=expected_columns))
    assert df.dtypes.iloc[0] == np.float32 # Check type of first column
    assert df.dtypes.iloc[-1] == np.float32 # Check type of last column (spectral)

def test_create_feature_row_empty_spectral_features():
    """Test creating a feature row with extra features but no spectral features."""
    features_dict = {}
    params = PreprocessingParameters(extra_features=True, target_bands=5) # Bands should be ignored
    
    df = create_feature_row(features_dict, params)
    
    expected_extra_cols = [
        "record_json_id", "original_file_ref", "fruit", "day", "side", 
        "camera_type", "ripeness_state", "ripeness_state_fine", "firmness", 
        "init_weight", "storage_days"
    ]
    expected_data = np.array([[np.nan] * len(expected_extra_cols)], dtype=np.float32)

    pd.testing.assert_frame_equal(df, pd.DataFrame(expected_data, columns=expected_extra_cols))
    assert df.dtypes.iloc[0] == np.float32

def test_create_feature_row_mismatched_band_length():
    """Test that ValueError is raised if spectral feature array length doesn't match target_bands."""
    features_dict = {ExtractionMethods.AVG_SPECTRUM: np.array([0.1, 0.2, 0.3])}
    params = PreprocessingParameters(extra_features=False, target_bands=2) # Expecting 2 bands, got 3
    
    with pytest.raises(ValueError, match="Feature 'avg_spectrum' array length .* does not match target_bands .*"):
        create_feature_row(features_dict, params)

def test_create_feature_row_zero_bands():
    """Test creating a feature row with zero bands."""
    features_dict = {ExtractionMethods.AVG_SPECTRUM: np.array([])}
    params = PreprocessingParameters(extra_features=False, target_bands=0)
    
    df = create_feature_row(features_dict, params)
    
    expected_columns = []
    expected_data = np.array([[]], dtype=np.float32) # Empty 2D array
    
    pd.testing.assert_frame_equal(df, pd.DataFrame(expected_data, columns=expected_columns))
    assert df.empty # Check if dataframe is empty