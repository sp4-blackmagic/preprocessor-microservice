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

    # Handle empty spectrum
    if spectrum.size == 0:
        print("Warning: The given spectrum is empty, continuum removal values will be invalid")
        return np.ones_like(spectrum)

    # Handle NaNs and Infs by interpolating/replacing them
    # Create a copy to avoid modifying the original input array in place if it's mutable
    processed_spectrum = spectrum.copy()
    
    # Identify non-finite values (NaNs or Infs)
    non_finite_mask = ~np.isfinite(processed_spectrum)
    
    # If all values are non-finite, give up (no interpolation possible)
    if np.all(non_finite_mask):
        print("Warning: All given spectrum values are non-finite, continuum removal values will be invalid")
        return np.ones_like(spectrum) 

    # If there are some non-finite values, interpolate them
    if np.any(non_finite_mask):
        x_coords_all = np.arange(len(processed_spectrum))
        x_coords_finite = x_coords_all[~non_finite_mask]
        
        # Only interpolate if there are finite points to interpolate from
        if len(x_coords_finite) > 1: # Need at least two finite points for interpolation
            processed_spectrum[non_finite_mask] = np.interp(
                x_coords_all[non_finite_mask], x_coords_finite, processed_spectrum[~non_finite_mask]
            )
        else: # If less than 2 finite points, cannot interpolate meaningfully
            print("Warning: Too many NaN values to interpolate, continuum removal values will be invalid")
            return np.ones_like(spectrum)

    # Now `processed_spectrum` should be finite and ready for continuum removal
    spectrum = processed_spectrum

    if not np.all(np.isfinite(spectrum)) or spectrum.size == 0:
        print("Warning: ")
        return np.ones_like(spectrum)

    if len(spectrum) != len(wavelengths_arr):
        min_len = min(len(spectrum), len(wavelengths_arr))
        spectrum, wavelengths_arr = spectrum[:min_len], wavelengths_arr[:min_len]

    if len(spectrum) < 3:
        print("Warning: Spectrum length below 3, continuum removal values will be invalid")
        return np.ones_like(spectrum)

    try:
        sort_indices = np.argsort(wavelengths_arr)
        wavelengths_sorted, spectrum_sorted = wavelengths_arr[sort_indices], spectrum[sort_indices]

        # Handle duplicate wavelengths (keep the highest value at a given wavelength)
        # This is important before building the hull
        processed_points_dict = {}
        for wl, val in zip(wavelengths_sorted, spectrum_sorted):
            processed_points_dict[wl] = max(processed_points_dict.get(wl, -np.inf), val)
        
        unique_wl_keys = np.array(sorted(processed_points_dict.keys()))
        unique_val_values = np.array([processed_points_dict[k] for k in unique_wl_keys])
        
        # These are the (wavelength, spectrum_value) points, unique by wavelength, sorted
        processed_points = np.vstack([unique_wl_keys, unique_val_values]).T

        if len(processed_points) < 2: # Need at least 2 points for a line
            print("Warning: Not enough points to form a line in continuum removal, continuum removal values will be invalid")
            return np.ones_like(spectrum)

        # Check for truly flat or linear spectrum (on the processed_points)
        if len(processed_points) >= 2:
            dx, dy = np.diff(processed_points[:, 0]), np.diff(processed_points[:, 1])
            non_zero_dx_mask = np.abs(dx) > 1e-9
            if np.any(non_zero_dx_mask):
                slopes = dy[non_zero_dx_mask] / dx[non_zero_dx_mask]
                if len(slopes) > 0 and np.allclose(slopes, slopes[0], atol=1e-9):
                    print("Warning: The spectrum is linear, continuum removal values will be invalid")
                    return np.ones_like(spectrum)
            elif np.all(dy == 0):
                print("Warning: The spectrum flat, continuum removal values will be invalid")
                return np.ones_like(spectrum)

        # Continuum Removal Rubber Band Algorithm
        # Iteratively find points that are above the line connecting the current hull points
        
        # Function to find the point furthest above a line
        def find_farthest_above(points_segment, p1_idx_in_segment, p2_idx_in_segment):
            p1 = points_segment[p1_idx_in_segment]
            p2 = points_segment[p2_idx_in_segment]
            
            # Line equation: y = m*x + c
            if p2[0] - p1[0] == 0: # Vertical line (shouldn't happen with sorted distinct wavelengths)
                return -1, -np.inf # No point is strictly above a vertical line in this context
            
            m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            c = p1[1] - m * p1[0]
            
            max_dist = -np.inf
            farthest_idx = -1
            
            # Iterate only through points *between* p1 and p2 in the segment
            for i in range(p1_idx_in_segment + 1, p2_idx_in_segment):
                p = points_segment[i]
                line_y = m * p[0] + c
                dist = p[1] - line_y # Distance from point to line (positive if above)
                if dist > max_dist:
                    max_dist = dist
                    farthest_idx = i
            return farthest_idx, max_dist

        # Build the upper hull recursively
        
        def build_hull(start_idx, end_idx):
            if start_idx == end_idx:
                return [start_idx] # Single point
            
            # Find the point furthest above the line (start_idx, end_idx)
            farthest_idx, max_dist = find_farthest_above(processed_points, start_idx, end_idx)
            
            if farthest_idx != -1 and max_dist > 1e-9: # If a significant point is found above the line
                # Recursively build hull for left segment
                left_segment_indices = build_hull(start_idx, farthest_idx)
                # Recursively build hull for right segment
                right_segment_indices = build_hull(farthest_idx, end_idx)
                return sorted(list(set(left_segment_indices + right_segment_indices))) # Combine and sort
            else:
                return [start_idx, end_idx] # Base case: no point found above, so the line is the hull

        # Start the recursive process
        initial_start_idx = 0
        initial_end_idx = len(processed_points) - 1
        
        # Get the indices of the hull points
        hull_point_indices_list = build_hull(initial_start_idx, initial_end_idx)
        
        # Extract the actual points and sort them by wavelength
        upper_hull_points_sorted = processed_points[hull_point_indices_list]
        upper_hull_points_sorted = upper_hull_points_sorted[np.argsort(upper_hull_points_sorted[:, 0])]

        hull_wl, hull_val = upper_hull_points_sorted[:, 0], upper_hull_points_sorted[:, 1]


        # Ensure at least 2 points for interpolation
        if len(hull_wl) < 2:
            print("Warning: Not enough points for interpolation, continuum removal values will be invalid")
            return np.ones_like(spectrum)

        # --- Interpolation and Division ---
        interp_func = interp1d(hull_wl, hull_val,
                               kind='linear', bounds_error=False, fill_value="extrapolate")
        continuum_line = interp_func(wavelengths_sorted)

        continuum_line[continuum_line <= 1e-9] = 1e-9

        continuum_removed_sorted = spectrum_sorted / continuum_line

        # --- Revert to original order and final NaN handling ---
        final_cr_original_order = np.zeros_like(spectrum, dtype=float)
        final_cr_original_order[sort_indices] = continuum_removed_sorted

        if np.isnan(final_cr_original_order).any():
            nan_mask = np.isnan(final_cr_original_order)
            x_coords = np.arange(len(wavelengths_arr))
            if np.any(~nan_mask):
                final_cr_original_order[nan_mask] = np.interp(x_coords[nan_mask], x_coords[~nan_mask], final_cr_original_order[~nan_mask])
            else:
                print("Warning: The final continuum removal values contain NaN values, continuum removal values will be invalid")
                return np.ones_like(spectrum)
        
        if np.isnan(final_cr_original_order).any():
            print("Warning: The final continuum removal values contain NaN values, continuum removal values will be invalid")
            return np.ones_like(spectrum)
        else:
            return final_cr_original_order

    except Exception as e:
        print(f"ERROR: Unhandled exception during continuum removal: {e}")
        raise e