import numpy as np
import pytest
from app.core.extraction import calculate_average_spectrum, calculate_continuum_removal

# ====================================
# Average Spectrum Calculation Testing
# ====================================

@pytest.fixture(
    params=[
        # Test Case 1: Simple 2D image with calculated mask
        (
            np.array([
                [0.1, 0.2, 0.3],
                [0.7, 0.8, 0.9],
                [0.0, 0.1, 0.2]
            ], dtype=np.float32),
            np.array([
                [False, False, False],
                [ True,  True,  True],
                [False, False, False]
            ], dtype=bool),
            np.array([0.8], dtype=np.float32)
        ),
        # Test Case 2: Simple 3D image, 3 bands, and a corresponding mask
        (
            np.array([
                [[0.1, 0.2, 0.0], [0.1, 0.2, 0.1]],
                [[0.7, 0.8, 0.6], [0.8, 0.9, 0.7]]
            ], dtype=np.float32),
            np.array([
                [False, False],
                [ True,  True]
            ], dtype=bool),
            np.array([0.75, 0.85, 0.65], dtype=np.float32)
        )
    ],
    ids=[
        "2D_simple",
        "3D_3_bands"
    ]
)
def average_spectrum_test_data(request):
    img_data, mask, expected_result = request.param
    return img_data, mask, expected_result

def test_average_spectrum_extraction(average_spectrum_test_data):
    img_data, mask, expected_result = average_spectrum_test_data
    result = calculate_average_spectrum(img_data=img_data, mask=mask)
    np.testing.assert_array_equal(result, expected_result)

def test_average_spectrum_no_mask():
    input = np.array([
        [0.1, 0.2, 0.3],
        [0.7, 0.8, 0.9],
        [0.3, 0.1, 0.2]
    ], dtype=np.float32)
    expected = np.array([0.4], dtype=np.float32).reshape(1, -1)
    np.testing.assert_array_equal(calculate_average_spectrum(input, None), expected)


def test_average_spectrum_no_input():
    with pytest.raises(ValueError, match="Input image data is None."):
        calculate_average_spectrum(None, None)

def test_average_spectrum_wrong_dimensions():
    # 1D array
    with pytest.raises(ValueError, match="Input image data must be 2D or 3D."):
        calculate_average_spectrum(np.array([1, 2, 3]), None)
    # 4D array
    with pytest.raises(ValueError, match="Input image data must be 2D or 3D."):
        calculate_average_spectrum(np.zeros((2, 2, 2, 2)), None)

# =====================================
# Continuum Removal Calculation Testing
# =====================================

@pytest.fixture(
    params=[
        # Test Case 1: Simple Absorption Feature (typical use case)
        (
            np.array([0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8]),
            np.array([500, 510, 520, 530, 540, 550, 560]),
            # Expected:
            # Hull points would be (500,0.8), (560,0.8)
            # Continuum line would be linear from 0.8 to 0.8 across the range (all 0.8s)
            # Result: spectrum / 0.8
            np.array([1.0, 0.875, 0.75, 0.625, 0.75, 0.875, 1.0])
        ),
        # Test Case 2: Rising Linear Spectrum (should return all ones)
        (
            np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            np.array([100, 110, 120, 130, 140]),
            # Expected: A linear spectrum's continuum is itself. So, CR should be all 1s.
            np.ones(5)
        ),
        # Test Case 3: Flat Spectrum (should return all ones)
        (
            np.array([0.5, 0.5, 0.5, 0.5, 0.5]),
            np.array([1, 2, 3, 4, 5]),
            np.ones(5)
        ),
        # Test Case 4: Spectrum with Wavelengths in Descending Order (should be sorted internally)
        (
            np.array([0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8]),
            np.array([560, 550, 540, 530, 520, 510, 500]), # Reversed wavelengths
            np.array([1.0, 0.875, 0.75, 0.625, 0.75, 0.875, 1.0])
        ),
        # Test Case 5: Spectrum with NaNs (should be filled with ones, or interpolated if partial)
        # Given the internal NaN handling, if ALL are NaN, returns ones.
        # If partial, interpolates. Let's test a partial NaN case.
        (
            np.array([0.8, np.nan, 0.6, 0.5, 0.6, np.nan, 0.8]),
            np.array([500, 510, 520, 530, 540, 550, 560]),
            np.array([1.0, 0.875, 0.75, 0.625, 0.75, 0.875, 1.0])
        ),
        # Test Case 6: Input spectrum size < 3 (should return all ones)
        (
            np.array([0.5, 0.6]),
            np.array([100, 110]),
            np.ones(2)
        ),
        # Test Case 7: Mismatching lengths (should truncate to min_len and return ones if < 3)
        (
            np.array([0.1, 0.2, 0.3, 0.4, 0.5]), # 5 elements
            np.array([100, 110]), # 2 elements
            np.ones(2) # Truncated to 2, then returns ones because len < 3
        ),
        # Test Case 8: Mismatching lengths (truncated but still >= 3)
        (
            np.array([0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8]), # 7 elements
            np.array([500, 510, 520, 530, 540]), # 5 elements
            # Truncated spectrum: [0.8, 0.7, 0.6, 0.5, 0.6]
            # Truncated wavelengths: [500, 510, 520, 530, 540]
            # Hull: (500,0.8), (540,0.6)
            # Continuum line: 0.8, 0.75, 0.7, 0.65, 0.6
            # CR: 0.8/0.8=1.0, 0.7/0.75=0.933, 0.6/0.7=0.857, 0.5/0.65=0.769, 0.6/0.6=1.0
            np.array([1.0, 0.93333333, 0.85714286, 0.76923077, 1.0])
        ),
        # Test Case 9: Spectrum with duplicate wavelengths (should handle via unique_idx and take max)
        (
            np.array([0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8]),
            np.array([500, 510, 520, 520, 540, 550, 560]), # Wavelength 520 is duplicated
            # Unique points after processing:
            # (500,0.8), (510,0.7), (520,0.6), (540,0.6), (550,0.7), (560,0.8)
            # (Note: for 520, 0.6 is higher than 0.5, so 0.6 is taken)
            # Hull should be (500,0.8) and (560,0.8)
            # Same as Test Case 1, as the duplicate 520,0.5 would be ignored anyway
            np.array([1.0, 0.875, 0.75, 0.625, 0.75, 0.875, 1.0])
        ),
        # Test Case 10: All infinite values (should return all ones)
        (
            np.array([np.inf, np.inf, np.inf]),
            np.array([1, 2, 3]),
            np.ones(3)
        ),
        # Test Case 11: All NaN values (should return all ones)
        (
            np.array([np.nan, np.nan, np.nan]),
            np.array([1, 2, 3]),
            np.ones(3)
        ),
        # Test Case 12: Empty spectrum (should return all ones)
        (
            np.array([]),
            np.array([]),
            np.ones(0) # Should return an empty array of ones (matching original empty spectrum)
        )
    ],
    ids=[
        "simple_absorption",
        "rising_linear_spectrum",
        "flat_spectrum",
        "wavelengths_descending_order",
        "spectrum_with_nan_partial_interp", # Failing
        "len_lt_3_points",
        "mismatch_len_truncate_lt_3",
        "mismatch_len_truncate_ge_3",
        "duplicate_wavelengths",
        "all_inf_values",
        "all_nan_values",
        "empty_spectrum"
    ]
)
def continuum_removal_test_data(request):
    """
    A pytest fixture providing various spectrums, wavelengths, and expected continuum-removed values
    for testing the calculate_continuum_removal function.
    """
    spectrum, wavelengths_arr, expected_cr_spectrum = request.param
    return spectrum, wavelengths_arr, expected_cr_spectrum

def test_calculate_continuum_removal_logic(continuum_removal_test_data):
    """
    Tests the main logic of calculate_continuum_removal using parameterized test data.
    Uses rtol and atol for floating-point comparisons.
    """
    spectrum, wavelengths_arr, expected_cr_spectrum = continuum_removal_test_data
    result_cr_spectrum = calculate_continuum_removal(spectrum, wavelengths_arr)

    # Use assert_allclose for floating-point comparisons
    np.testing.assert_allclose(result_cr_spectrum, expected_cr_spectrum, rtol=1e-5, atol=1e-8)
    assert result_cr_spectrum.dtype == np.float64 