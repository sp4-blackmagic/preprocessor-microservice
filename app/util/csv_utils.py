import io
import csv
import numpy as np
import pandas as pd
from app.schemas.data_models import PreprocessingParameters

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

def create_feature_row(features_dict_array: [dict], params: PreprocessingParameters):
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
    if len(features_dict_array) == 0:
        raise ValueError(f"Empty features_dict_array provided.")

    # Sanity check
    for features_dict in features_dict_array:
        for key, value in features_dict.items():
            if len(value) != params.target_bands:
                raise ValueError(f"Feature '{key.value}' array length {len(value)} does not match target_bands {params.target_bands}")

    column_names = []
    dummy_extra_values = []

    # Handle Extra Features (Metadata)
    if params.extra_features:
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

    for key in features_dict_array[0].keys():
        column_names.extend([f"{key.value}_b{i}" for i in range(params.target_bands)])

    data = []
    for features_dict in features_dict_array:
        feature_values_list = []
        feature_values_list.extend(dummy_extra_values)
        for value_array in features_dict.values():
            # For example: "avg_spectrum0", "avg_spectrum1", ..., "avg_spectrum223"
            feature_values_list.extend(value_array.tolist())

        data.append(np.array(feature_values_list, dtype=np.float32))

    df = pd.DataFrame(data, columns=column_names)

    return df