from app.util.cube_slicer import *
import numpy as np
import pytest

@pytest.fixture(params=[
        # empty mask for entire cube
        (
            np.array([
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2]],
                [[0.3, 0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.9, 0.5]]
            ], dtype=np.float32), # original datacube
            [0,0,2,2],
            np.array([
                [0.0, 0.0],
                [0.0, 0.0]
            ], dtype=np.float32), # mask
            np.array([
                [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]],
                [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]]
            ], dtype=np.float32), # expected
        ),
        # regular expected scenario
        (
            np.array([
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2]],
                [[0.3, 0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.9, 0.5]]
            ], dtype=np.float32), # original datacube
            [0,0,1,2],
            np.array([
                [1.0, 0.0],
                [1.0, 0.0]
            ], dtype=np.float32), # mask
            np.array([
                [[0.1, 0.1, 0.1, 0.1, 0.1]],
                [[0.3, 0.3, 0.3, 0.3, 0.3]]
            ], dtype=np.float32), # expected
        ),
        # regular expected scenario, but with having to have zeros in some places
        (
            np.array([
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2], [0.2, 0.1, 0.3, 0.9, 0.2]],
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2], [0.2, 0.7, 0.3, 0.5, 0.4]],
                [[0.3, 0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.9, 0.5], [0.8, 0.8, 0.3, 0.9, 0.7]]
            ], dtype=np.float32), # original datacube
            [1,0,3,3],
            np.array([
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 1.0],
                [0.0, 1.0, 0.0]
            ], dtype=np.float32), # mask
            np.array([
                [[0.0, 0.0, 0.0, 0.0, 0.0], [0.2, 0.1, 0.3, 0.9, 0.2]],
                [[0.2, 0.2, 0.2, 0.2, 0.2], [0.2, 0.7, 0.3, 0.5, 0.4]],
                [[0.4, 0.4, 0.4, 0.9, 0.5], [0.0, 0.0, 0.0, 0.0, 0.0]]
            ], dtype=np.float32), # expected
        ),
        # box not fully containing mask
        (
            np.array([
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2], [0.2, 0.1, 0.3, 0.9, 0.2]],
                [[0.1, 0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2, 0.2], [0.2, 0.7, 0.3, 0.5, 0.4]],
                [[0.3, 0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.9, 0.5], [0.8, 0.8, 0.3, 0.9, 0.7]]
            ], dtype=np.float32), # original datacube
            [0,1,2,3],
            np.array([
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 1.0],
                [0.0, 1.0, 0.0]
            ], dtype=np.float32), # mask
            np.array([
                [[0.0, 0.0, 0.0, 0.0, 0.0], [0.2, 0.2, 0.2, 0.2, 0.2]],
                [[0.0, 0.0, 0.0, 0.0, 0.0], [0.4, 0.4, 0.4, 0.9, 0.5]]
            ], dtype=np.float32), # expected
        )
    ]
)
def cubes_boxes_masks(request):
    original_cube, box, mask, expected_cube = request.param
    return original_cube, box, mask, expected_cube

def test_extract_shape(cubes_boxes_masks):
    original_cube, box, mask, expected_cube = cubes_boxes_masks
    extracted_shape = extract_shape(original_cube, box, mask)
    np.testing.assert_array_equal(extracted_shape, expected_cube)
    assert expected_cube.dtype == np.float32

#def test_get_kiwis_zeros():
#    data = np.zeros((15, 15, 40), dtype=np.float32)
#
#    result = get_kiwis(data)
#
#    assert len(result) == 0

def test_get_kiwis_not_enough_bands():
    data = np.random.rand(1500, 800, 20).astype(np.float32)

    with pytest.raises(ValueError, match="29 bands"):
        get_kiwis(data)