import numpy as np
import tempfile
import shutil
import spectral.io.envi as envi
import os
from numpy import ndarray
from scipy.signal import savgol_filter
from fastapi import UploadFile, File
from spectral.io.envi import EnviDataFileNotFoundError
from app.schemas.data_models import PreprocessingParameters, ExtractionMethods
from app.schemas.exceptions import InvalidFileFormatError, DataProcessingError, BackgroundRemovalError, MissingMetadataError
from app.util.background_removal import calculate_simple_background_mask
from app.core.extraction import calculate_average_spectrum, calculate_continuum_removal
from app.core.resampling import resample_img_data, resize_wavelengths
from app.util.csv_utils import create_feature_row
from app.util.validation import basic_file_validation
from spectral.io.envi import SpectralLibrary
from spectral import SpyFile

async def preprocess(
    hdr_file: UploadFile = File(...),
    cube_file: UploadFile = File(...), 
    params: PreprocessingParameters = PreprocessingParameters()
):
    temp_hdr_path = None
    temp_cube_path = None

    try:
        # Sanity check
        basic_file_validation(hdr_file=hdr_file, cube_file=cube_file)

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

        try:
            # Open the image using spectral and extract reflectance
            # envi.open will throw an exception if the header file is
            # in non-ENVI format
            img: SpyFile | SpectralLibrary = envi.open(temp_hdr_path, temp_cube_path)
            img_data: ndarray = img.load().astype(np.float32)
            print(f"The parsed image has {img.nrows} rows, {img.ncols} columns, and {img.nbands} bands")
            print(f"The image takes up approximately {np.round(4 * img.nrows * img.ncols * img.nbands / 1024 / 1024 * 1000) / 100} MB of memory")

            # ===============
            # File Resampling
            # ===============

            # Get the original wavelength values for later resampling
            original_wavelengths = None
            print("=== wavelengths ===")
            print(img.bands.band_unit)
            if(hasattr(img, "spectra")): print(img.spectra)
            else: print("no spectra")
            if hasattr(img, "metadata") and "wavelength" in img.metadata and img.metadata["wavelength"]: 
                try:
                    # Ensure the wavelengths are loaded in as float values
                    original_wavelengths = np.array([float(w) for w in img.metadata["wavelength"]])
                    if len(original_wavelengths) != img.nbands:
                        raise MissingMetadataError(detail="Wavelength array lenght in the header file does not match the number of bands.")
                except ValueError:
                    raise MissingMetadataError(detail="Wavelengths in the header file are not valid numbers.")
            else: 
                # If no wavelengths are provided in the header file, assume
                # default spectrum based on the min/max_wavelength parameters
                original_wavelengths = np.linspace(params.min_wavelength, params.max_wavelength, img.nbands) 
                print("Warning: No wavelengths found in HDR. Using min_wavelength and max_wavelength from parameters to generate a default spectrum")

            # Get the target wavelengths from original
            target_wavelengths = resize_wavelengths(original_wavelengths=original_wavelengths, target_bands=params.target_bands)

            # Resample the data to fit target dimensions
            img_data = resample_img_data(
                img_data=img_data,
                original_wavelengths=original_wavelengths,
                target_wavelengths=target_wavelengths,
                kind=params.resampling_kind
            )

            # Check if the resampling was successful
            if img_data.shape[2] != params.target_bands:
                raise DataProcessingError(detail="Resampling failed to produce the target number of bands")
            
            # ==================
            # Background Removal
            # ==================

            # Get the mask to remove background
            mask = calculate_simple_background_mask(img_data)
            if params.remove_background and np.sum(mask) == 0:
                raise BackgroundRemovalError(detail="Background removal resulted in an empty image (all pixels removed). Adjust threshold or disable.")

            # ================
            # Extract Features
            # ================

            extracted_features = dict()
            
            # Average Spectrum (calculating it anyways because its used in other methods)
            avg_spectrum = calculate_average_spectrum(img_data=img_data, mask=mask)
            if ExtractionMethods.AVG_SPECTRUM in params.extraction_methods:
                extracted_features[ExtractionMethods.AVG_SPECTRUM] = avg_spectrum


            # 1st Derivative of Average Spectrum
            if ExtractionMethods.FIRST_DERIV_AVG_SPECTRUM in params.extraction_methods:
                if params.target_bands > params.sg_window_deriv and params.sg_window_deriv > params.sg_polyorder_deriv:
                    extracted_features[ExtractionMethods.FIRST_DERIV_AVG_SPECTRUM] = savgol_filter(avg_spectrum, params.sg_window_deriv, params.sg_polyorder_deriv, deriv=1) if params.target_bands > params.sg_window_deriv else np.zeros_like(avg_spectrum)
                else:
                    raise DataProcessingError(detail="Savitzky-Golay filter parameters are invalid. Expected values: target_bands > sg_window_deriv < sg_polyorder_deriv")
        
            # Continuum Removed from Average Spectrum (also calculating anyways because its used in other methods)
            cr_avg_spectrum = calculate_continuum_removal(avg_spectrum, target_wavelengths)
            if ExtractionMethods.CONTINUUM_REMOVED_AVG_SPECTRUM in params.extraction_methods:
                extracted_features[ExtractionMethods.CONTINUUM_REMOVED_AVG_SPECTRUM] = cr_avg_spectrum

            # Standard Normal Variate of Average Spectrum
            if ExtractionMethods.SNV_AVG_SPECTRUM in params.extraction_methods:
                if np.std(avg_spectrum) > (1e-9):
                    extracted_features[ExtractionMethods.SNV_AVG_SPECTRUM] = (avg_spectrum - np.mean(avg_spectrum)) / np.std(avg_spectrum)
                else:
                    print("Warning: Standard deviation near zero, values might be unreliable")
                    extracted_features[ExtractionMethods.SNV_AVG_SPECTRUM] = avg_spectrum - np.mean(avg_spectrum)

            # 1st Derivative of Continuum Removed Spectrum
            if ExtractionMethods.FIRST_DERIV_CONTINUUM_REMOVED_AVG_SPECTRUM in params.extraction_methods:
                if params.target_bands > params.sg_window_deriv and params.sg_window_deriv > params.sg_polyorder_deriv:
                    extracted_features[ExtractionMethods.FIRST_DERIV_CONTINUUM_REMOVED_AVG_SPECTRUM] = savgol_filter(cr_avg_spectrum, params.sg_window_deriv, params.sg_polyorder_deriv, deriv=1) if params.target_bands > params.sg_window_deriv else np.zeros_like(cr_avg_spectrum)
                else:
                    raise DataProcessingError(detail="Savitzky-Golay filter parameters are invalid. Expected values: target_bands > sg_window_deriv < sg_polyorder_deriv")

            # ===================================================
            # Create and return DataFrame from extracted features
            # ===================================================

            # Sanity check
            if not extracted_features:
                raise DataProcessingError(detail="No extraction methods were selected or produced valid features.")

            return create_feature_row(extracted_features, params)
        
        except EnviDataFileNotFoundError as e:
            raise InvalidFileFormatError(detail=f"Error caused by non-ENVI header file. Exception: {e}")
        except BackgroundRemovalError as e:
            raise e
        except MissingMetadataError as e:
            raise e
        except Exception as e:
            raise DataProcessingError(detail=f"Unexpected error occurred during processing. Exception: {e}")

    finally:
        # Clean up temporary files
        if temp_hdr_path and os.path.exists(temp_hdr_path):
            os.unlink(temp_hdr_path)
        if temp_cube_path and os.path.exists(temp_cube_path):            
            os.unlink(temp_cube_path)

        # Close file streams
        if hasattr(hdr_file, "file") and hdr_file.file:
            await hdr_file.close()
        if hasattr(cube_file, "file") and cube_file.file:
            await cube_file.close()
    