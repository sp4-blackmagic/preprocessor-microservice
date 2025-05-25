import numpy as np
import pandas as pd
import tempfile
import shutil
import spectral.io.envi as envi
from numpy import ndarray
import os
from fastapi import UploadFile, File
from app.schemas.data_models import PreprocessingParameters
from app.util.background_removal import calculate_simple_background_mask
from app.core.extraction import calculate_average_spectrum


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

    # ====================================
    # Extract Reflectances and Count Means
    # ====================================

    try:
        # Open the image using spectral and extract reflectance
        # since we are using files in the ENVI format, I am using
        # the spectral.io.envi function, and not the general spectral.open_image
        img = envi.open(temp_hdr_path, temp_cube_path)
        img_data: ndarray = img.load().astype(np.float32)
        print(f"The parsed image has {img.nrows} rows, {img.ncols} columns, and {img.nbands} bands")
        print(f"The image takes up approximately {4 * img.nrows * img.ncols * img.nbands / 1024 / 1024} MB of memory")

        mask = calculate_simple_background_mask(img_data)

        # Extract Average Spectrum
        extracted = calculate_average_spectrum(img_data=img_data, mask=mask)
        print(extracted)

        # Create and return a .csv response file
        column_names = [f"avg_spectrum_b{i}" for i in range(0, img.nbands)]
        df = pd.DataFrame(extracted, columns=column_names)

        return df

    except Exception as e:
        # TODO: Handle exceptions here
        print(f"Error occured during data preprocessing! Exception: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(temp_hdr_path):
            os.unlink(temp_hdr_path)
        if os.path.exists(temp_cube_path):            
            os.unlink(temp_cube_path)
        await hdr_file.close()
        await cube_file.close()
    