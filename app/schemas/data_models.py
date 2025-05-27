from pydantic import BaseModel, Field
from fastapi import Form, HTTPException
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import json

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
    extra_features: bool = False # Whether to include the features like "original_file_ref" and so on, look for extracted_features_VIS_test_unbalanced for the idea
    target_bands: int = 224 
    resampling_kind: str = "linear"
    min_wavelength: int = 470
    max_wavelength: int = 900
    sg_window_deriv: int = 11
    sg_polyorder_deriv: int = 2 

# Helper function to pass fields from PreprocessingParameters as single inputs in a multipart/form-data request
async def get_preprocessing_params(
    # Each field from the Pydantic model now becomes a Form() parameter
    # with its default and type hints directly from the Pydantic model..
    extraction_methods: Optional[str] = Form(None), # JSON string for list
    remove_background: bool = Form(PreprocessingParameters.model_fields['remove_background'].default),
    background_treshold: float = Form(PreprocessingParameters.model_fields['background_treshold'].default),
    extra_features: bool = Form(PreprocessingParameters.model_fields['extra_features'].default),
    target_bands: int = Form(PreprocessingParameters.model_fields['target_bands'].default),
    resampling_kind: str = Form(PreprocessingParameters.model_fields['resampling_kind'].default),
    min_wavelength: int = Form(PreprocessingParameters.model_fields['min_wavelength'].default),
    max_wavelength: int = Form(PreprocessingParameters.model_fields['max_wavelength'].default),
    sg_window_deriv: int = Form(PreprocessingParameters.model_fields['sg_window_deriv'].default),
    sg_polyorder_deriv: int = Form(PreprocessingParameters.model_fields['sg_polyorder_deriv'].default)
) -> PreprocessingParameters:
    # Manually parse the extraction_methods if it's a JSON string
    parsed_extraction_methods = None
    if extraction_methods:
        try:
            parsed_list = json.loads(extraction_methods)
            parsed_extraction_methods = [ExtractionMethods(m) for m in parsed_list]
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON for extraction_methods")
        except ValueError as e: # If string doesn't match an Enum member
            raise HTTPException(status_code=400, detail=f"Invalid extraction method value: {e}")

    # Construct the Pydantic model instance
    params_data = {
        "remove_background": remove_background,
        "background_treshold": background_treshold,
        "extra_features": extra_features,
        "target_bands": target_bands,
        "resampling_kind": resampling_kind,
        "min_wavelength": min_wavelength,
        "max_wavelength": max_wavelength,
        "sg_window_deriv": sg_window_deriv,
        "sg_polyorder_deriv": sg_polyorder_deriv
    }
    if parsed_extraction_methods is not None:
        params_data["extraction_methods"] = parsed_extraction_methods

    return PreprocessingParameters(**params_data)
