"""
Simple test script to verify Cellpose integration works
"""
import numpy as np
import torch
from cellpose.models import CellposeModel

def test_cellpose():
    print("Testing Cellpose integration...")

    # Create a synthetic test image (512x512 RGB)
    print("Creating synthetic test image...")
    test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)

    # Add some "cell-like" circular blobs
    y, x = np.ogrid[:512, :512]
    for i in range(10):
        center_y, center_x = np.random.randint(100, 400, 2)
        radius = np.random.randint(20, 40)
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        test_image[mask] = [200, 200, 200]

    print(f"Test image shape: {test_image.shape}")

    # Initialize model
    print("Initializing Cellpose model (CPU)...")
    device = torch.device("cpu")
    model = CellposeModel(
        device=device,
        pretrained_model="cpsam",
        use_bfloat16=False
    )
    print("Model initialized successfully!")

    # Run segmentation
    print("Running segmentation (this may take 30-60 seconds)...")
    masks, flows, styles = model.eval(
        test_image,
        batch_size=4,
        diameter=30,
        flow_threshold=0.4,
        cellprob_threshold=0.0,
        normalize=True,
        min_size=15,
        resample=False,
        augment=False
    )

    # Calculate coverage
    total_pixels = masks.shape[0] * masks.shape[1]
    cell_pixels = np.sum(masks > 0)
    coverage_percent = (cell_pixels / total_pixels) * 100
    num_cells = len(np.unique(masks)) - 1

    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    print(f"Image size: {masks.shape}")
    print(f"Cells detected: {num_cells}")
    print(f"Cell pixels: {cell_pixels:,}")
    print(f"Total pixels: {total_pixels:,}")
    print(f"Coverage: {coverage_percent:.2f}%")
    print("="*50)
    print("\nTest completed successfully!")

    return True

if __name__ == "__main__":
    test_cellpose()
