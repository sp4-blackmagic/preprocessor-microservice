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

def get_kiwis(originial_data: ndarray):
    (rows, cols, bands) = originial_data.shape

    print("running model")
    # converting to image and running YOLO model
    results = []
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp_file:
        spectral.save_rgb(tmp_file.name, originial_data, [29, 19, 9])
        results = model(tmp_file.name)
    r = results[0]

    kiwi_slices = []

    print("getting kiwis")
    for i, box in enumerate(r.boxes.xyxy):
        (x1, y1, x2, y2) = map(int, box.tolist())
        kiwi_height = y2-y1
        kiwi_width = x2-x1

        kiwi_cube = np.zeros((kiwi_height, kiwi_width, bands), dtype=np.float32)

        mask_np = r.masks[i].data[0].cpu().numpy()

        #saving mask
        #mask_image = Image.fromarray((mask_np * 255).astype(np.uint8))
        #mask_image.save(f"mask_output{i}.png")

        height_scaler = YOLO_SIDE_LENGTH//rows
        width_scaler = YOLO_SIDE_LENGTH//cols

        for j in range(kiwi_height):
            for k in range(kiwi_width):
                if mask_np[(j+y1)*height_scaler,(k+x1)*width_scaler] == 1.0:
                    kiwi_cube[j, k] = data[j+y1, k+x1]

        kiwi_slices.append(kiwi_cube)

        #spectral.envi.save_image(f'kiwi_{i}.hdr', kiwi_cube, interleave='bsq', force=True)
        #spectral.save_rgb(f'cropped_{i}.jpg', kiwi_cube, [29, 19, 9])
    
    return kiwi_slices


