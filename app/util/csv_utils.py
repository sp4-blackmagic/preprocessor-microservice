import io
import csv
import numpy as np
import pandas as pd
from typing import Set, List
from app.schemas.data_models import ExtractionMethods, PreprocessingParameters

def read_csv(csv_bytes: bytes, encoding: str):
    """
    Returns a csv._reader object from given data
    in bytes format
    
    Parameters
    ----------
    csv_bytes: bytes
        Bytes of the csv file
    encoding: str
        Type of encoding to use while converting
        the csv bytes to strings
    """
    csv_string = csv_bytes.decode(encoding)
    csv_file = io.StringIO(csv_string)
    csv_reader = csv.reader(csv_file)
    return csv_reader

def generate_headers(extraction_methods: Set[ExtractionMethods], bands: int, include_extras: bool):
    """
    Returns a list of strings meant to serve as headers for the spectral
    data preprocessing response
    
    Parameters
    ----------
    extraction_methods: Set[ExtractionMethods]
        A set of enum values describing which extraction methods
        to include in the generated headers
    bands: int
        Number of bands for which to generate the headers
    include_extras: bool
        Boolean indicating whether the generated headers
        should include additional fields that were created
        during data exploration, which are:
        - record_json_id
        - original_file_ref
        - fruit
        - day
        - side
        - camera_type
        - ripeness_state
        - firmness
        - int_weight
        - storage_days
        Most if not all of these fields will be set to null
    """
    headers: List[str] = []

    if include_extras:
        headers.append("record_json_id")
        headers.append("original_file_ref")
        headers.append("fruit")
        headers.append("day")
        headers.append("side")
        headers.append("camera_type")
        headers.append("ripeness_state")
        headers.append("ripeness_state_fine")
        headers.append("firmness")
        headers.append("init_weight")
        headers.append("storage_days")

    for method in extraction_methods:
        for i in range(0, bands):
            header = method.value + "_b" + str(i)
            headers.append(header)

    return headers

def create_feature_row(features_dict: dict, params: PreprocessingParameters):
    """
    Creates a single row (1D NumPy array) of features and corresponding column names
    by horizontally concatenating extra features and extracted spectral features.

    Args:
        extracted_features_dict (dict): A dictionary where keys are feature names
                                        (e.g., 'avg_spectrum', 'first_deriv') and
                                        values are 1D NumPy arrays of spectral data.
                                        Example: {'avg_spectrum': np.array([...]),
                                                  'first_deriv': np.array([...])}
        params: An object with attributes like `extra_features` (bool) and `target_bands` (int).

    Returns:
        pd.DataFrame: A DataFrame with a single row containing all concatenated features.
    """

    feature_values_list = []
    column_names = []

    # 1. Handle Extra Features (Metadata)
    if params.extra_features:
        # Define the names for the extra features
        extra_feature_names = [
            "record_json_id",
            "original_file_ref",
            "fruit",
            "day",
            "side",
            "camera_type",
            "ripeness_state",
            "ripeness_state_fine",
            "firmness",
            "init_weight",
            "storage_days"
        ]
        column_names.extend(extra_feature_names)

        # Append dummy values for extra features to the list of values
        # These None values will become NaN when converted to float32
        dummy_extra_values = [None] * len(extra_feature_names)
        feature_values_list.extend(dummy_extra_values)

    for key, value_array in features_dict.items():
        # For example: "avg_spectrum0", "avg_spectrum1", ..., "avg_spectrum223"
        column_names.extend([f"{key.value}_b{i}" for i in range(params.target_bands)])
        feature_values_list.extend(value_array.tolist())

    data_row = np.array(feature_values_list, dtype=np.float32).reshape(1, -1)

    # 5. Create the Pandas DataFrame
    df = pd.DataFrame(data_row, columns=column_names)

    return df