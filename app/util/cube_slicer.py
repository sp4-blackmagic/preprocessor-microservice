# keep this as first import because otherwise YOLO breaks for some reason
from ultralytics import YOLO
import spectral
import numpy as np
from numpy import ndarray
import tempfile
from pathlib import Path

base_path = Path(__file__).resolve().parent

YOLO_SIDE_LENGTH = 512
print("loading yolo model")
model = YOLO(base_path / "model/best.pt")

def extract_shape(original_data: ndarray, box: list[int], mask: ndarray):
    (rows, cols, bands) = original_data.shape
    (mask_rows, mask_cols) = mask.shape

    (x1, y1, x2, y2) = box
    shape_height = y2-y1
    shape_width = x2-x1

    shape_cube = np.zeros((shape_height, shape_width, bands), dtype=np.float32)

    #saving mask
    #mask_image = Image.fromarray((mask_np * 255).astype(np.uint8))
    #mask_image.save(f"mask_output{i}.png")

    height_scaler = mask_rows/rows
    width_scaler = mask_cols/cols

    for j in range(shape_height):
        for k in range(shape_width):
            if mask[int((j+y1)*height_scaler),int((k+x1)*width_scaler)] == 1.0:
                shape_cube[j, k] = original_data[j+y1, k+x1]

    return shape_cube

def get_kiwis(original_data: ndarray):
    if original_data.shape[2] <= 29:
        raise ValueError("Input data must have at least 29 bands to extract RGB channels.")
    
    print("running model")
    # converting to image and running YOLO model
    results = []
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp_file:
        spectral.save_rgb(tmp_file.name, original_data, [29, 19, 9])
        results = model(tmp_file.name)
    r = results[0]

    kiwi_slices = []

    print("getting kiwis")
    for i, box in enumerate(r.boxes.xyxy):
        kiwi_slices.append(
            extract_shape(
                original_data,
                map(int, box.tolist()),
                r.masks[i].data[0].cpu().numpy()
            )
        )
    
    return kiwi_slices