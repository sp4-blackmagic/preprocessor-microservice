from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Set
from enum import Enum

class ExtractionMethods(Enum):
    AVG_SPECTRUM = "avg_spectrum"
    FIRST_DERIV_AVG_SPECTRUM = "deriv1_avg_spectrum"
    CONTINUUM_REMOVED_AVG_SPECTRUM = "continuum_removed_avg_spectrum"
    SNV_AVG_SPECTRUM  = "snv_avg_spectrum"
    FIRST_DERIV_CONTINUUM_REMOVED_AVG_SPECTRUM = "deriv1_continuum_removed"


class PreprocessingParameters(BaseModel):
    extraction_methods: List[ExtractionMethods] = list(dict.fromkeys([
        ExtractionMethods.AVG_SPECTRUM,
        ExtractionMethods.FIRST_DERIV_AVG_SPECTRUM,
        ExtractionMethods.CONTINUUM_REMOVED_AVG_SPECTRUM,
        ExtractionMethods.SNV_AVG_SPECTRUM,
        ExtractionMethods.FIRST_DERIV_CONTINUUM_REMOVED_AVG_SPECTRUM
    ]))
    remove_background: bool = False
    background_treshold: float = 0.1
    extra_features: bool = True  # Whether to include the features like "original_file_ref" and so on, look for extracted_features_VIS_test_unbalanced for the idea
    target_bands: int = 224
    resampling_kind: str = "linear"
    min_wavelength: int = 470
    max_wavelength: int = 900
    sg_window_deriv: int = 11
    sg_polyorder_deriv: int = 2