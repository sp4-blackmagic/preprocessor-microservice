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
    bands: int = 224