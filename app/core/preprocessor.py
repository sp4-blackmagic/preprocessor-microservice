# =======================
# Libraries and constants
# =======================
import numpy as np
import argparse
import spectral
from spectral import SpyFile
import os
import sys
import csv
from fastapi import UploadFile, File
from app.schemas.data_models import PreprocessingParameters

# ====================
# Function Definitoins
# ====================

def extract_reflectance(path: str) -> SpyFile:
    img = spectral.open_image(path)
    reflectance_data = img.load()
    return reflectance_data

def read_wavelengths(img: SpyFile, lower: int, upper: int):
    wavelengths = np.linspace(lower, upper, num=img.nbands)  
    return wavelengths

def preprocess(hdr_file: UploadFile = File(...), cube_file: UploadFile = File(...), params: PreprocessingParameters = PreprocessingParameters()):
    # ====================================
    # Extract Reflectances and Count Means
    # ====================================

    print(f"Trying to extract reflectance data from '{hdr_path}'...")
    img = extract_reflectance(path=hdr_path)
    print(f"The parsed image has {img.nrows} rows, {img.ncols} columns, and {img.nbands} bands")


    lower_wv_bound = float(args.wv_lower_bound)
    upper_wv_bound = float(args.wv_upper_bound)
    wavelengths = read_wavelengths(img=img, lower=lower_wv_bound, upper=upper_wv_bound)
    print(f"Created {img.bands} bands between the wavelengths {lower_wv_bound} and {upper_wv_bound}")

    print("Calculating the mean reflectance for each wavelength band...")
    mean_reflectances = dict()
    for i in range(0, img.nrows):
        for j in range(0, img.ncols):
            for k in range(0, img.nbands):
                if wavelengths[k] in mean_reflectances:
                    mean_reflectances[wavelengths[k]] += img[i, j, k]
                else:
                    mean_reflectances[wavelengths[k]] = img[i, j, k]

    for wv in wavelengths:
        mean_reflectances[wv] /= img.nrows * img.ncols
        print(f"Wavelength: {wv}, Mean Reflectance: {mean_reflectances[wv]}")

    # =================
    # Saving the Output
    # =================

    # Generate a name for the csv file
    csv_name = ""
    if args.label == None:
        csv_name = "unknown"
    else:
        csv_name = str(args.label)

    file_number = 1
    csv_path = f"{csv_dir}/{csv_name}_{file_number}.csv"
    while os.path.isfile(csv_path):
        file_number += 1

    # Save the csv file
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(wavelengths)
        writer.writerow(mean_reflectances.values())

    print(f"Saved the results to '{csv_path}'")