"""
Example script showing how to use the Cellpose Freestyle app programmatically.
This demonstrates the core functionality without needing to run the web server.
"""

import numpy as np
from PIL import Image
import sys
import os

# Add parent directory to path to import cellpose
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cellpose import models, utils


def create_sample_image():
    """Create a simple synthetic cell image for testing."""
    # Create a 512x512 image with synthetic cells
    img = np.zeros((512, 512), dtype=np.uint8)

    # Add some circular "cells"
    from scipy.ndimage import gaussian_filter

    # Create random cell centers
    np.random.seed(42)
    n_cells = 20

    for i in range(n_cells):
        # Random position and size
        x, y = np.random.randint(50, 462, 2)
        radius = np.random.randint(15, 30)

        # Create circular mask
        yy, xx = np.ogrid[:512, :512]
        circle = (xx - x)**2 + (yy - y)**2 <= radius**2

        # Add to image with some intensity variation
        img[circle] = np.random.randint(150, 255)

    # Apply Gaussian blur for smoother cells
    img = gaussian_filter(img.astype(float), sigma=2)
    img = (img * 255 / img.max()).astype(np.uint8)

    return img


def example_basic_segmentation():
    """Example 1: Basic cell segmentation and counting."""
    print("="*60)
    print("Example 1: Basic Cell Segmentation")
    print("="*60)

    # Load model
    print("Loading Cellpose model...")
    model = models.CellposeModel(gpu=False, pretrained_model="cpsam")

    # Create or load image
    print("Creating sample image...")
    img = create_sample_image()

    # Run segmentation
    print("Running segmentation...")
    masks, flows, styles = model.eval(
        img,
        diameter=None,  # Auto-detect
        flow_threshold=0.4,
        cellprob_threshold=0.0,
        batch_size=8
    )

    # Count cells
    n_cells = masks.max()
    print(f"✓ Detected {n_cells} cells")

    # Save results
    print("Saving results...")
    Image.fromarray(img).save("example_input.png")
    Image.fromarray((masks > 0).astype(np.uint8) * 255).save("example_masks.png")

    print("✓ Saved: example_input.png, example_masks.png")
    print()


def example_cell_analysis():
    """Example 2: Detailed cell analysis with measurements."""
    print("="*60)
    print("Example 2: Detailed Cell Analysis")
    print("="*60)

    # Load model
    model = models.CellposeModel(gpu=False, pretrained_model="cpsam")

    # Create sample image
    img = create_sample_image()

    # Run segmentation
    print("Running segmentation...")
    masks, flows, styles = model.eval(img)

    # Perform analyses
    print("\nCell Measurements:")
    print("-" * 40)

    # Count
    n_cells = masks.max()
    print(f"  Cell count: {n_cells}")

    # Diameters
    diameters = utils.diameters(masks)
    print(f"  Mean diameter: {np.mean(diameters):.1f} pixels")
    print(f"  Diameter range: {np.min(diameters):.1f} - {np.max(diameters):.1f} pixels")

    # Compactness (roundness)
    compactness = utils.get_mask_compactness(masks)
    print(f"  Mean roundness: {np.mean(compactness):.2f} (1.0 = perfect circle)")

    # Perimeters
    perimeters = utils.get_mask_perimeters(masks)
    print(f"  Mean perimeter: {np.mean(perimeters):.1f} pixels")

    print()


def example_custom_parameters():
    """Example 3: Using custom parameters for specific cell types."""
    print("="*60)
    print("Example 3: Custom Parameters for Dead/Dim Cells")
    print("="*60)

    # Load model
    model = models.CellposeModel(gpu=False, pretrained_model="cpsam")

    # Create sample image with dimmer cells
    img = create_sample_image()
    img_dim = (img * 0.5).astype(np.uint8)  # Make cells dimmer

    # Standard parameters
    print("Running with standard parameters...")
    masks_standard, _, _ = model.eval(
        img_dim,
        cellprob_threshold=0.0  # Default
    )
    n_standard = masks_standard.max()
    print(f"  Detected {n_standard} cells")

    # Lower threshold for dim cells
    print("Running with lower threshold (for dead/dim cells)...")
    masks_dim, _, _ = model.eval(
        img_dim,
        cellprob_threshold=-2.0  # Lower threshold
    )
    n_dim = masks_dim.max()
    print(f"  Detected {n_dim} cells")

    print(f"\n  → Lower threshold detected {n_dim - n_standard} additional dim cells")
    print()


def example_visualization():
    """Example 4: Creating visualization overlays."""
    print("="*60)
    print("Example 4: Visualization with Outlines")
    print("="*60)

    # Load model
    model = models.CellposeModel(gpu=False, pretrained_model="cpsam")

    # Create sample image
    img = create_sample_image()

    # Run segmentation
    print("Running segmentation...")
    masks, flows, styles = model.eval(img)

    # Create visualization
    print("Creating visualization...")

    # Get outlines
    outlines = utils.masks_to_outlines(masks)

    # Create RGB overlay
    overlay = np.stack([img, img, img], axis=-1)
    overlay[outlines > 0] = [255, 0, 0]  # Red outlines

    # Save
    Image.fromarray(overlay).save("example_overlay.png")
    print("✓ Saved: example_overlay.png")
    print()


def example_agent_simulation():
    """Example 5: Simulating the AI agent's query interpretation."""
    print("="*60)
    print("Example 5: AI Agent Query Interpretation (Simulated)")
    print("="*60)

    queries = [
        "count the cells in this image",
        "count the dead cells",
        "measure cell sizes",
        "find only large cells",
        "analyze cell shape and roundness"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        print("  Interpretation:")

        if "dead" in query.lower() or "dim" in query.lower():
            print("    → cellprob_threshold: -2.0 (lower for dim cells)")

        if "large" in query.lower():
            print("    → min_size: 50 (filter for larger cells)")

        if "size" in query.lower() or "measure" in query.lower():
            print("    → analyses: ['count', 'diameter']")

        if "shape" in query.lower() or "round" in query.lower():
            print("    → analyses: ['count', 'compactness']")

        if "count" in query.lower() and len(query.split()) <= 6:
            print("    → analyses: ['count']")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Cellpose Freestyle - Example Usage")
    print("="*60 + "\n")

    try:
        # Check if scipy is available for sample image generation
        try:
            import scipy
        except ImportError:
            print("Note: scipy not installed. Using simple sample images.")
            print("Install scipy for better examples: pip install scipy\n")

        # Run examples
        example_basic_segmentation()
        example_cell_analysis()
        example_custom_parameters()
        example_visualization()
        example_agent_simulation()

        print("="*60)
        print("All examples completed successfully!")
        print("="*60)
        print("\nGenerated files:")
        print("  - example_input.png")
        print("  - example_masks.png")
        print("  - example_overlay.png")
        print("\nTo run the full web app:")
        print("  1. cd app")
        print("  2. pip install -r requirements.txt")
        print("  3. export ANTHROPIC_API_KEY='your-key' (optional)")
        print("  4. python backend.py")
        print("  5. Open http://localhost:5000")
        print()

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
