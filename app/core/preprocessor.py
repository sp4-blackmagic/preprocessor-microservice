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

def preprocess():

    # ==============
    # Argparse Setup
    # ==============

    parser = argparse.ArgumentParser(prog=__name__,
                                     description="Converts a .hdr file obtained"
                                     "from the imec hyperspectral camera"
                                     "into a csv containing reflectance data")
    parser.add_argument("sample_hdr_path", help="The path to the sample .hdr file to be parsed")
    parser.add_argument("label", help="Label of the provided sample")
    parser.add_argument("csv_directory_path", help="The directory in which to save the .csv file with reflectance data")
    parser.add_argument("--wv_lower_bound", default=400, type=float)
    parser.add_argument("--wv_upper_bound", default=900, type=float)
    args = parser.parse_args()

    # ==================
    # Resolve File Paths
    # ==================

    # Check if the samples exist at provided path
    hdr_path = os.path.abspath(args.sample_hdr_path)
    raw_path = hdr_path[:hdr_path.index('.')] + ".raw"
    files_exist = True
    if not os.path.isfile(hdr_path):
        print(f"The hdr sample file at path '{hdr_path}' does not exist!")
        files_exist = False
    if not os.path.isfile(raw_path):
        print(f"The raw sample file at path '{raw_path}' does not exist!")
        files_exist = False
    if not files_exist:
        print(f"Could not resolve some file paths. Exiting program.")
        sys.exit()

    # Check if the output file directory exists
    csv_dir = os.path.abspath(args.csv_directory_path)
    if not os.path.isdir(csv_dir):
        print(f"Directory at path {csv_dir} does not exist!")
        sys.exit()

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