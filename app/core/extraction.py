import numpy as np
from typing import Optional
from numpy import ndarray


def calculate_average_spectrum(img_data: ndarray, mask: Optional[ndarray]):
    if img_data is None: raise ValueError("Input image data is None.")
    if img_data.ndim < 2 or img_data.ndim > 3: raise ValueError("Input image data must be 2D or 3D.")
    if mask is None:
        # If no mask provided, just create a sample mask that will 
        # accept all values as true
        if img_data.ndim == 3: mask = np.full(img_data.shape[:-1], True, dtype=bool)
        else: mask = np.full(img_data.shape, True, dtype=bool)

    avg_spectra = np.mean(img_data[mask], axis=0)
    return avg_spectra
