import numpy as np
import pandas as pd
import tempfile
import shutil
import spectral.io.envi as envi
from spectral.io.envi import SpectralLibrary, BilFile, BipFile, BsqFile
import os
from fastapi import UploadFile, File
from app.schemas.data_models import PreprocessingParameters

# async def extract_reflectance(path: str) -> SpyFile:
#     img = spectral.open_image(path)
#     reflectance_data = img.load()
#     return reflectance_data

# def read_wavelengths(img: SpyFile, lower: int, upper: int):
#     wavelengths = np.linspace(lower, upper, num=img.nbands)  
#     return wavelengths

    # print("Calculating the mean reflectance for each wavelength band...")
    # mean_reflectances = dict()
    # for i in range(0, img.nrows):
    #     for j in range(0, img.ncols):
    #         for k in range(0, img.nbands):
    #             if wavelengths[k] in mean_reflectances:
    #                 mean_reflectances[wavelengths[k]] += img[i, j, k]
    #             else:
    #                 mean_reflectances[wavelengths[k]] = img[i, j, k]

    # for wv in wavelengths:
    #     mean_reflectances[wv] /= img.nrows * img.ncols
    #     print(f"Wavelength: {wv}, Mean Reflectance: {mean_reflectances[wv]}")

def calculate_average_spectrum(hyperspectral_image: SpectralLibrary | BilFile | BipFile | BsqFile):
    avg_spectra = list()
    bands = hyperspectral_image.nbands
    for i in range(0, bands):
        image = hyperspectral_image.read_band(i)
        avg_spectra.append(0)
        for row in image:
            for val in row:
                avg_spectra[i] += val
                
        avg_spectra[i] /= hyperspectral_image.nrows * hyperspectral_image.ncols

    # Reshape into a 2D array so it can be converted into a DataFrame
    return np.array(avg_spectra).reshape(1, -1)


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
        print(f"The parsed image has {img.nrows} rows, {img.ncols} columns, and {img.nbands} bands")
        print(f"The image takes up approximately {4 * img.nrows * img.ncols * img.nbands / 1024 / 1024} MB of memory")
        
        # # Find the minimum and maximum wavelength values
        # wavelengths: list[float] = []
        # for wv in img.metadata["wavelength"]:
        #     wavelengths.append(float(wv))
            
        # min_wv = min(wavelengths)
        # max_wv = max(wavelengths)
        # print(f"The wavelength values are between {min_wv}nm and {max_wv}nm")

        # Extract Average Spectrum
        extracted = calculate_average_spectrum(hyperspectral_image=img)

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
    

    # print(f"Trying to extract reflectance data from '{hdr_path}'...")
    # img = extract_reflectance(path=hdr_path)
    # print(f"The parsed image has {img.nrows} rows, {img.ncols} columns, and {img.nbands} bands")


    # lower_wv_bound = float(args.wv_lower_bound)
    # upper_wv_bound = float(args.wv_upper_bound)
    # wavelengths = read_wavelengths(img=img, lower=lower_wv_bound, upper=upper_wv_bound)
    # print(f"Created {img.bands} bands between the wavelengths {lower_wv_bound} and {upper_wv_bound}")



    # # =================
    # # Saving the Output
    # # =================

    # # Generate a name for the csv file
    # csv_name = ""
    # if args.label == None:
    #     csv_name = "unknown"
    # else:
    #     csv_name = str(args.label)

    # file_number = 1
    # csv_path = f"{csv_dir}/{csv_name}_{file_number}.csv"
    # while os.path.isfile(csv_path):
    #     file_number += 1

    # # Save the csv file
    # with open(csv_path, mode="w", newline="") as file:
    #     writer = csv.writer(file)
    #     writer.writerow(wavelengths)
    #     writer.writerow(mean_reflectances.values())

    # print(f"Saved the results to '{csv_path}'")