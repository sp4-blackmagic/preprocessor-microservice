import numpy as np
from typing import Optional
from numpy import ndarray
from scipy.spatial import ConvexHull
from scipy.interpolate import interp1d


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

def calculate_continuum_removal(spectrum, wavelengths_arr):
    if not isinstance(spectrum, np.ndarray): spectrum = np.array(spectrum)
    if not isinstance(wavelengths_arr, np.ndarray): wavelengths_arr = np.array(wavelengths_arr)
    if not np.all(np.isfinite(spectrum)) or spectrum.size == 0: return np.ones_like(spectrum)
    if len(spectrum) != len(wavelengths_arr):
        min_len = min(len(spectrum), len(wavelengths_arr))
        spectrum, wavelengths_arr = spectrum[:min_len], wavelengths_arr[:min_len]
    if len(spectrum) < 3: return np.ones_like(spectrum)
    try:
        sort_indices = np.argsort(wavelengths_arr)
        wavelengths_sorted, spectrum_sorted = wavelengths_arr[sort_indices], spectrum[sort_indices]
        points = np.vstack([wavelengths_sorted, spectrum_sorted]).T
        unique_wl, unique_idx = np.unique(points[:, 0], return_index=True)
        points = points[unique_idx]
        if len(points) < 3: return np.ones_like(spectrum)
        if len(points) >= 2:
            dx, dy = np.diff(points[:, 0]), np.diff(points[:, 1])
            slopes = dy / (dx + 1e-9)
            if len(slopes) > 0 and np.allclose(slopes, slopes[0]): return np.ones_like(spectrum)
        hull = ConvexHull(points, qhull_options='QJ'); hull_indices = hull.vertices
        upper_hull_points_sorted = points[hull_indices][np.argsort(points[hull_indices, 0])]
        hull_wl, hull_val = upper_hull_points_sorted[:, 0], upper_hull_points_sorted[:, 1]
        if wavelengths_sorted[0] not in hull_wl:
            hull_wl, hull_val = np.insert(hull_wl, 0, wavelengths_sorted[0]), np.insert(hull_val, 0, spectrum_sorted[0])
            sort_again = np.argsort(hull_wl); hull_wl, hull_val = hull_wl[sort_again], hull_val[sort_again]
        if wavelengths_sorted[-1] not in hull_wl:
            hull_wl, hull_val = np.append(hull_wl, wavelengths_sorted[-1]), np.append(hull_val, spectrum_sorted[-1])
            sort_again = np.argsort(hull_wl); hull_wl, hull_val = hull_wl[sort_again], hull_val[sort_again]
        temp_dict = {}
        for i_wl, i_val in zip(hull_wl, hull_val): temp_dict[i_wl] = max(temp_dict.get(i_wl, -np.inf), i_val)
        unique_final_hull_wl = np.array(sorted(temp_dict.keys()))
        unique_final_hull_val = np.array([temp_dict[wl_key] for wl_key in unique_final_hull_wl])
        if len(unique_final_hull_wl) < 2: return np.ones_like(spectrum)
        interp_func = interp1d(unique_final_hull_wl, unique_final_hull_val, kind='linear', bounds_error=False, fill_value="extrapolate")
        continuum_line = interp_func(wavelengths_sorted)
        continuum_line[continuum_line <= 1e-9] = 1e-9
        continuum_removed_sorted = spectrum_sorted / continuum_line
        final_cr_original_order = np.zeros_like(spectrum); final_cr_original_order[sort_indices] = continuum_removed_sorted
        if np.isnan(final_cr_original_order).any():
            nan_mask = np.isnan(final_cr_original_order); x_coords = np.arange(len(wavelengths_arr))
            if np.any(~nan_mask): final_cr_original_order[nan_mask] = np.interp(x_coords[nan_mask], x_coords[~nan_mask], final_cr_original_order[~nan_mask])
            else: return np.ones_like(spectrum)
        return np.ones_like(spectrum) if np.isnan(final_cr_original_order).any() else final_cr_original_order
    except Exception: return np.ones_like(spectrum)
