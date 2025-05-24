import numpy as np
from numpy import ndarray


def calculate_simple_background_mask(img_data: ndarray, threshold: float = 0.1):
    if img_data is None: raise ValueError("Input image data is None.")
    if img_data.ndim == 3:
        if img_data.shape[-1] == 0: return np.zeros(img_data.shape[:2], dtype=bool)
        band_idx_for_intensity = img_data.shape[-1] * 3 // 4
        if band_idx_for_intensity >= img_data.shape[-1]: band_idx_for_intensity = img_data.shape[-1] // 2
        intensity_band = np.squeeze(img_data[:, :, band_idx_for_intensity])
    elif img_data.ndim == 2: intensity_band = img_data
    else: raise ValueError(f"Input image data must be 2D or 3D. Got {img_data.ndim}D with shape {img_data.shape}")
    if intensity_band.size == 0: return np.array([], dtype=bool)
    min_val, max_val = np.min(intensity_band), np.max(intensity_band)
    if max_val == min_val: return np.ones_like(intensity_band, dtype=bool) if min_val > 0 else np.zeros_like(intensity_band, dtype=bool)
    intensity_norm = (intensity_band - min_val) / (max_val - min_val + 1e-9)
    return intensity_norm > threshold