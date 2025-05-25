import numpy as np
import pandas as pd
import tempfile
import shutil
import spectral.io.envi as envi
from numpy import ndarray
from scipy.signal import savgol_filter
import os
from fastapi import UploadFile, File
from app.schemas.data_models import PreprocessingParameters, ExtractionMethods
from app.util.background_removal import calculate_simple_background_mask
from app.core.extraction import calculate_average_spectrum, calculate_continuum_removal
from app.core.resampling import resample_img_data, resize_wavelengths
from app.util.csv_utils import create_feature_row

async def preprocess(
    hdr_file: UploadFile = File(...),
    cube_file: UploadFile = File(...), 
    params: PreprocessingParameters = PreprocessingParameters()
):
    # ================================================
    # Prepare uploaded files to be handled by spectral
    # ================================================

    # Create a temporary .hdr file in storage
    with tempfile.NamedTemporaryFile(delete=False, suffix=".hdr") as temp_hdr:
        shutil.copyfileobj(hdr_file.file, temp_hdr)
        temp_hdr_path = temp_hdr.name

    # Ensure both the .hdr and .bin/.raw files have the same file name
    cube_suffix = cube_file.filename.split(".")[-1].lower()
    base_name = temp_hdr_path.rsplit('.', 1)[0]
    temp_cube_path = f"{base_name}.{cube_suffix}"

    # Create a temporary .bin/.raw file in storage
    with open(temp_cube_path, "wb") as temp_cube:
        shutil.copyfileobj(cube_file.file, temp_cube)

    # ===========================
    # Open file and resample data
    # ===========================

    try:
        # Open the image using spectral and extract reflectance
        # since we are using files in the ENVI format, I am using
        # the spectral.io.envi function, and not the general spectral.open_image
        img = envi.open(temp_hdr_path, temp_cube_path)
        img_data: ndarray = img.load().astype(np.float32)
        print(f"The parsed image has {img.nrows} rows, {img.ncols} columns, and {img.nbands} bands")
        print(f"The image takes up approximately {4 * img.nrows * img.ncols * img.nbands / 1024 / 1024} MB of memory")

        # Get the original wavelength values for later resampling
        original_wavelengths = None
        if hasattr(img, "metadata") and "wavelengths" in img.metadata: original_wavelengths = img.metadata["wavelengths"]
        else: original_wavelengths = np.linspace(params.min_wavelength, params.max_wavelength, img.nbands) # No wavelength values provided, assume default spectrum

        # Get the target wavelengths from original
        target_wavelengths = resize_wavelengths(original_wavelengths=original_wavelengths, target_bands=params.target_bands)

        # Resample the data to fit target dimensions
        img_data = resample_img_data(
            img_data=img_data,
            original_wavelengths=original_wavelengths,
            target_wavelengths=target_wavelengths,
            kind=params.resampling_kind
        )

        # Get the mask to remove background
        mask = calculate_simple_background_mask(img_data)

        # ================
        # Extract Features
        # ================

        extracted_features = dict()
        
        # Average Spectrum
        # Calculating it anyways because its used in other methods
        print("avg")
        avg_spectrum = calculate_average_spectrum(img_data=img_data, mask=mask)
        if ExtractionMethods.AVG_SPECTRUM in params.extraction_methods:
            extracted_features[ExtractionMethods.AVG_SPECTRUM] = avg_spectrum
        print("first")
        # 1st Derivative of Average Spectrum
        if ExtractionMethods.FIRST_DERIV_AVG_SPECTRUM in params.extraction_methods:
            extracted_features[ExtractionMethods.FIRST_DERIV_AVG_SPECTRUM] = savgol_filter(avg_spectrum, params.sg_window_deriv, params.sg_polyorder_deriv, deriv=1) if params.target_bands > params.sg_window_deriv else np.zeros_like(avg_spectrum)
        print("continuum")
        # Continuum Removed from Average Spectrum
        # Calculating anyways because its used in other methods
        cr_avg_spectrum = calculate_continuum_removal(avg_spectrum, target_wavelengths)
        if ExtractionMethods.CONTINUUM_REMOVED_AVG_SPECTRUM in params.extraction_methods:
            extracted_features[ExtractionMethods.CONTINUUM_REMOVED_AVG_SPECTRUM] = cr_avg_spectrum
        print("snv")
        # Standard Normal Variate of Average Spectrum
        if ExtractionMethods.SNV_AVG_SPECTRUM in params.extraction_methods:
            if np.std(avg_spectrum) > (1e-9):
                extracted_features[ExtractionMethods.SNV_AVG_SPECTRUM] = (avg_spectrum - np.mean(avg_spectrum)) / np.std(avg_spectrum)
            else:
                extracted_features[ExtractionMethods.SNV_AVG_SPECTRUM] = avg_spectrum - np.mean(avg_spectrum)
        print("last")
        # 1st Derivative of Continuum Removed Spectrum
        if ExtractionMethods.FIRST_DERIV_CONTINUUM_REMOVED_AVG_SPECTRUM in params.extraction_methods:
            extracted_features[ExtractionMethods.FIRST_DERIV_CONTINUUM_REMOVED_AVG_SPECTRUM] = savgol_filter(cr_avg_spectrum, params.sg_window_deriv, params.sg_polyorder_deriv, deriv=1) if params.target_bands > params.sg_window_deriv else np.zeros_like(cr_avg_spectrum)

        # ===================================================
        # Create and return DataFrame from extracted features
        # ===================================================

        return create_feature_row(extracted_features, params)

    except Exception as e:
        # TODO: Handle exceptions here
        raise Exception(f"Internal error occured during data preprocessing! Exception: {e}.")
        # if isinstance(e, AttributeError):
        #     raise AttributeError(f"Exception: Wrong .hdr file format. Only ENVI header files are supported.")
        # else:
    finally:
        # Clean up temporary files
        if os.path.exists(temp_hdr_path):
            os.unlink(temp_hdr_path)
        if os.path.exists(temp_cube_path):            
            os.unlink(temp_cube_path)
        await hdr_file.close()
        await cube_file.close()
    