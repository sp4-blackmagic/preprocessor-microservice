import pytest
import numpy as np
from app.core.resampling import resample_img_data

@pytest.fixture
def mismatched_resampling_data():
    # There are 3 bands in the array and 
    # 50 bands in the original_wavelengths
    return (
        np.array([
            [[0.1, 0.2, 0.0], [0.1, 0.2, 0.1]],
            [[0.7, 0.8, 0.6], [0.8, 0.9, 0.7]]
        ], dtype=np.float32),
        np.linspace(470, 900, 50),
        np.linspace(470, 900, 100)
    )

@pytest.fixture(
    params=[
        # Test Case 1: Extrapolate a 100x100 image from 50 to 100 bands
        # band_idx_for_intensity = 3 * 3 // 4 = 2
        (
            np.random.rand(100, 100, 50).astype(np.float32) * 0.8 + 0.1, # Random 100x100 reflectance data
            np.linspace(470, 900, 50), # Sample wavelength values
            np.linspace(470, 900, 100) # Wavelengths to extrapolate to
        ),
        # Test Case 2: Interpolate a 100x100 image from 100 to 50 bands
        (
            np.random.rand(100, 100, 100).astype(np.float32) * 0.8 + 0.1, # Random 100x100 reflectance data
            np.linspace(470, 900, 100), # Sample wavelength values
            np.linspace(470, 900, 50) # Wavelengths to interpolate to
        )
    ],
    ids=[
        "extrapolate_from_50_to_100",
        "interpolate_from_100_to_50"
    ]
)
def resampling_test_data(request):
    img_data, original_wavelengths, target_wavelengths = request.param
    return img_data, original_wavelengths, target_wavelengths

def test_resampling_mismatched_dimensions(mismatched_resampling_data):
    img_data, original_wavelengths, target_wavelenghts = mismatched_resampling_data
    with pytest.raises(ValueError):
        resampled = resample_img_data(
            img_data=img_data,
            original_wavelengths=original_wavelengths,
            target_wavelengths=target_wavelenghts,
            kind="linear"
        )

def test_resampling_interpolate_and_extrapolate(resampling_test_data):
    img_data, original_wavelengths, target_wavelengths = resampling_test_data
    resampled = resample_img_data(
        img_data=img_data,
        original_wavelengths=original_wavelengths,
        target_wavelengths=target_wavelengths,
        kind="linear"
    )
    expected_shape = img_data.shape[:-1] + (len(target_wavelengths),)
    assert resampled.shape == expected_shape
    assert np.all(resampled < 10) and np.all(resampled > -10) # pretty generous reflectance value check