import io
import csv
from typing import Set, List
from app.schemas.data_models import ExtractionMethods

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