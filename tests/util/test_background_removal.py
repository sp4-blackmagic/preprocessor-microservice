from app.util.background_removal import calculate_simple_background_mask
import numpy as np
import pytest

@pytest.fixture(
    params=[
        # Test Case 1: Simple 2D image, clear foreground/background
        (
            np.array([
                [0.1, 0.2, 0.3],
                [0.7, 0.8, 0.9],
                [0.0, 0.1, 0.2]
            ], dtype=np.float32),
            0.5, # threshold
            np.array([
                [False, False, False],
                [ True,  True,  True],
                [False, False, False]
            ], dtype=bool)
        ),
        # Test Case 2: Simple 3D image, 3 bands, threshold applies to band 3//4 = band 2 (0-indexed)
        # band_idx_for_intensity = 3 * 3 // 4 = 2
        (
            np.array([
                [[0.1, 0.2, 0.0], [0.1, 0.2, 0.1]],
                [[0.7, 0.8, 0.6], [0.8, 0.9, 0.7]]
            ], dtype=np.float32),
            0.5, # threshold
            np.array([
                [False, False],
                [ True,  True]
            ], dtype=bool)
        ),
        # Test Case 3: 3D image, 1 band (should be treated as 2D)
        (
            np.array([
                [[0.1], [0.8]],
                [[0.2], [0.9]]
            ], dtype=np.float32),
            0.7, # threshold
            np.array([
                [False,  True],
                [False,  True]
            ], dtype=bool)
        ),
        # Test Case 4: All values below threshold in a 2D image
        (
            np.array([
                [0.01, 0.02],
                [0.03, 0.04]
            ], dtype=np.float32),
            0.1, # threshold
            np.array([
                [False, False],
                [False, False]
            ], dtype=bool)
        ),
        # Test Case 5: All values above threshold (or equal) in a 2D image
        (
            np.array([
                [0.6, 0.7],
                [0.8, 0.9]
            ], dtype=np.float32),
            0.5, # threshold
            np.array([
                [ True,  True],
                [ True,  True]
            ], dtype=bool)
        ),
        # Test Case 6: 2D image with all same non-zero values (should return all True)
        (
            np.array([
                [0.5, 0.5],
                [0.5, 0.5]
            ], dtype=np.float32),
            0.1, # threshold (doesn't matter here due to max_val == min_val handling)
            np.array([
                [ True,  True],
                [ True,  True]
            ], dtype=bool)
        ),
        # Test Case 7: 2D image with all zero values (should return all False)
        (
            np.array([
                [0.0, 0.0],
                [0.0, 0.0]
            ], dtype=np.float32),
            0.1,
            np.array([
                [False, False],
                [False, False]
            ], dtype=bool)
        ),
        # Test Case 8: 3D image with 5 bands. 5 * 3 // 4 = 3. Band 3 (0-indexed) will be used.
        (
            np.array([
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2]],
                [[0.3, 0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.9, 0.5]] # Band 3 (0.9) will be selected
            ], dtype=np.float32),
            0.5, # threshold
            np.array([
                [False, False],
                [False,  True]
            ], dtype=bool)
        ),
        # Test Case 9: 3D image with 0 bands (should return all False spatial dimensions)
        (
            np.zeros((5, 5, 0), dtype=np.float32),
            0.5,
            np.zeros((5, 5), dtype=bool)
        )
    ],
    ids=[
        "2D_clear_fgbg",
        "3D_3bands_mid_intensity",
        "3D_1band_as_2D",
        "2D_all_below_thresh",
        "2D_all_above_thresh",
        "2D_all_same_nonzero",
        "2D_all_zeros",
        "3D_5bands_specific_band_selection",
        "3D_0bands"
    ]
)
def background_removal_test_data(request):
    """
    A pytest fixture providing various image data, thresholds, and expected masks
    for testing the simple_background_removal function.
    """
    img_data, threshold, expected_mask = request.param
    return img_data, threshold, expected_mask

def test_simple_background_removal_logic(background_removal_test_data):
    """
    Tests the main logic of simple_background_removal using parameterized test data.
    """
    img_data, threshold, expected_mask = background_removal_test_data
    result_mask = calculate_simple_background_mask(img_data, threshold)
    np.testing.assert_array_equal(result_mask, expected_mask)
    assert result_mask.dtype == bool

def test_simple_background_removal_none_input():
    """
    Tests that simple_background_removal raises ValueError for None input.
    """
    with pytest.raises(ValueError, match="Input image data is None."):
        calculate_simple_background_mask(None)

def test_simple_background_removal_invalid_dimensions():
    """
    Tests that simple_background_removal raises ValueError for invalid input dimensions.
    """
    # 1D array
    with pytest.raises(ValueError, match="Input image data must be 2D or 3D."):
        calculate_simple_background_mask(np.array([1, 2, 3]))
    # 4D array
    with pytest.raises(ValueError, match="Input image data must be 2D or 3D."):
        calculate_simple_background_mask(np.zeros((2, 2, 2, 2)))