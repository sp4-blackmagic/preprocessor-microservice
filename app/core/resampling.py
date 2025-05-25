import numpy as np
from scipy.interpolate import interp1d

def resample_img_data(
    img_data: np.ndarray,
    original_wavelengths: np.ndarray,
    target_bands: int,
    kind: str = 'linear'
) -> np.ndarray: 
    """
    Resamples a 3D hyperspectral data cube along the band (wavelength) dimension.

    Args:
        reflectance_data_3d (np.ndarray): The input 3D reflectance data with shape
                                          (height, width, original_num_bands).
        original_wavelengths (np.ndarray): 1D array of original wavelength values.
        target_wavelengths (np.ndarray): 1D array of target wavelength values
                                         for resampling.
        kind (str): The type of interpolation to use (e.g., 'linear', 'cubic').

    Returns:
        np.ndarray: The resampled 3D reflectance data with shape
                    (height, width, target_num_bands).
    """
    height, width, bands = img_data.shape
    min_wv = np.min(original_wavelengths)
    max_wv = np.max(original_wavelengths)
    target_wavelengths = np.linspace(min_wv, max_wv, target_bands)

    # Validate input dimensions
    if bands != len(original_wavelengths):
        raise ValueError(
            f"Number of bands in img_data ({bands}) "
            f"does not match the length of original_wavelengths ({len(original_wavelengths)})."
        )
    
    # Pre-allocate memory for the resampled data
    resampled_img_data = np.zeros((height, width, target_bands), dtype=img_data.dtype)

    # Resample the band reflectance range for one pixel at a time
    for r in range(height):
        for c in range(width):
            pixel_spectrum = img_data[r, c, :]

            resample_func = interp1d(
                original_wavelengths, 
                pixel_spectrum,
                kind=kind,
                bounds_error=False,
                fill_value="extrapolate"
            )

            # Resample the pixel's spectrum 
            resampled_pixel_spectrum = resample_func(target_wavelengths)

            resampled_img_data[r, c, :] = resampled_pixel_spectrum

    return resampled_img_data