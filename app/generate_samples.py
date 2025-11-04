#!/usr/bin/env python
"""
Generate sample cell images for testing the Cellpose Freestyle app.
Creates synthetic cell images with various characteristics.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


def create_sample_cells_basic(width=512, height=512, n_cells=25, seed=42):
    """Create a basic synthetic cell image."""
    np.random.seed(seed)
    img = np.zeros((height, width), dtype=np.float32)

    for i in range(n_cells):
        # Random position (avoid edges)
        x = np.random.randint(40, width - 40)
        y = np.random.randint(40, height - 40)

        # Random size
        radius = np.random.randint(12, 25)

        # Create circular mask
        yy, xx = np.ogrid[:height, :width]
        circle = (xx - x)**2 + (yy - y)**2 <= radius**2

        # Add with intensity variation
        intensity = np.random.uniform(180, 255)
        img[circle] = np.maximum(img[circle], intensity)

    # Add Gaussian blur
    from scipy.ndimage import gaussian_filter
    img = gaussian_filter(img, sigma=1.5)

    # Add noise
    noise = np.random.normal(0, 5, img.shape)
    img = np.clip(img + noise, 0, 255)

    return img.astype(np.uint8)


def create_sample_cells_dense(width=512, height=512, n_cells=50, seed=123):
    """Create a dense/crowded cell image."""
    np.random.seed(seed)
    img = np.zeros((height, width), dtype=np.float32)

    for i in range(n_cells):
        x = np.random.randint(30, width - 30)
        y = np.random.randint(30, height - 30)
        radius = np.random.randint(10, 20)

        yy, xx = np.ogrid[:height, :width]
        circle = (xx - x)**2 + (yy - y)**2 <= radius**2

        intensity = np.random.uniform(150, 255)
        img[circle] = np.maximum(img[circle], intensity)

    from scipy.ndimage import gaussian_filter
    img = gaussian_filter(img, sigma=1.5)
    noise = np.random.normal(0, 8, img.shape)
    img = np.clip(img + noise, 0, 255)

    return img.astype(np.uint8)


def create_sample_cells_dim(width=512, height=512, n_cells=20, seed=456):
    """Create a dim/dead cell image (lower intensity)."""
    np.random.seed(seed)
    img = np.zeros((height, width), dtype=np.float32)

    for i in range(n_cells):
        x = np.random.randint(40, width - 40)
        y = np.random.randint(40, height - 40)
        radius = np.random.randint(12, 22)

        yy, xx = np.ogrid[:height, :width]
        circle = (xx - x)**2 + (yy - y)**2 <= radius**2

        # Dimmer intensity for "dead" cells
        intensity = np.random.uniform(80, 140)
        img[circle] = np.maximum(img[circle], intensity)

    from scipy.ndimage import gaussian_filter
    img = gaussian_filter(img, sigma=2.0)
    noise = np.random.normal(0, 10, img.shape)
    img = np.clip(img + noise, 0, 255)

    return img.astype(np.uint8)


def create_sample_cells_varied(width=512, height=512, seed=789):
    """Create cells with varied sizes (small and large)."""
    np.random.seed(seed)
    img = np.zeros((height, width), dtype=np.float32)

    # Add some small cells
    for i in range(15):
        x = np.random.randint(30, width - 30)
        y = np.random.randint(30, height - 30)
        radius = np.random.randint(8, 15)

        yy, xx = np.ogrid[:height, :width]
        circle = (xx - x)**2 + (yy - y)**2 <= radius**2
        intensity = np.random.uniform(180, 255)
        img[circle] = np.maximum(img[circle], intensity)

    # Add some large cells
    for i in range(8):
        x = np.random.randint(50, width - 50)
        y = np.random.randint(50, height - 50)
        radius = np.random.randint(25, 40)

        yy, xx = np.ogrid[:height, :width]
        circle = (xx - x)**2 + (yy - y)**2 <= radius**2
        intensity = np.random.uniform(180, 255)
        img[circle] = np.maximum(img[circle], intensity)

    from scipy.ndimage import gaussian_filter
    img = gaussian_filter(img, sigma=1.5)
    noise = np.random.normal(0, 6, img.shape)
    img = np.clip(img + noise, 0, 255)

    return img.astype(np.uint8)


def add_label(img_array, text, position='top'):
    """Add a text label to an image."""
    # Convert to PIL for text rendering
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fall back to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font = ImageFont.load_default()

    # Calculate position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if position == 'top':
        x = (img.width - text_width) // 2
        y = 10
    else:  # bottom
        x = (img.width - text_width) // 2
        y = img.height - text_height - 10

    # Draw white background rectangle
    draw.rectangle([x-5, y-2, x+text_width+5, y+text_height+2], fill=(255, 255, 255))

    # Draw text
    draw.text((x, y), text, fill=(0, 0, 0), font=font)

    return np.array(img)


def main():
    """Generate all sample images."""
    print("="*60)
    print("Generating Sample Cell Images")
    print("="*60)
    print()

    # Check if scipy is available
    try:
        import scipy
    except ImportError:
        print("Error: scipy is required for generating sample images")
        print("Install with: pip install scipy")
        return

    # Create samples directory
    samples_dir = "sample_images"
    os.makedirs(samples_dir, exist_ok=True)

    samples = [
        {
            "name": "basic_cells.png",
            "description": "Basic (25 cells, normal intensity)",
            "generator": create_sample_cells_basic,
            "params": {"n_cells": 25, "seed": 42}
        },
        {
            "name": "dense_cells.png",
            "description": "Dense (50 crowded cells)",
            "generator": create_sample_cells_dense,
            "params": {"n_cells": 50, "seed": 123}
        },
        {
            "name": "dim_cells.png",
            "description": "Dim/Dead (20 low-intensity cells)",
            "generator": create_sample_cells_dim,
            "params": {"n_cells": 20, "seed": 456}
        },
        {
            "name": "varied_cells.png",
            "description": "Varied Sizes (small and large cells)",
            "generator": create_sample_cells_varied,
            "params": {"seed": 789}
        }
    ]

    for sample in samples:
        print(f"Creating {sample['name']}...")
        print(f"  Description: {sample['description']}")

        # Generate image
        img = sample["generator"](**sample["params"])

        # Add label
        # img = add_label(img, sample['description'].split('(')[0].strip())

        # Save
        filepath = os.path.join(samples_dir, sample["name"])
        Image.fromarray(img).save(filepath)

        print(f"  ✓ Saved to {filepath}")
        print()

    print("="*60)
    print("Sample Generation Complete!")
    print("="*60)
    print()
    print(f"Generated {len(samples)} sample images in '{samples_dir}/'")
    print()
    print("You can now use these images to test the app:")
    print("  1. Run: python backend.py")
    print("  2. Open: http://localhost:5000")
    print("  3. Upload images from sample_images/")
    print()
    print("Suggested queries to try:")
    print("  - 'Count the cells' (basic_cells.png)")
    print("  - 'Count the cells in crowded areas' (dense_cells.png)")
    print("  - 'Count the dead cells' (dim_cells.png)")
    print("  - 'Find only the large cells' (varied_cells.png)")
    print()


if __name__ == "__main__":
    main()
