import numpy as np
import pytest
from app.core.extraction import calculate_average_spectrum

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