"""
Cellpose Cell Coverage Analyzer Web Application

A Flask web app that analyzes cell coverage in microscopy images using Cellpose.
"""

from flask import Flask, render_template, request, jsonify
import os
import numpy as np
from PIL import Image
import io
import base64
import torch
from cellpose.models import CellposeModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global model instance (loaded once)
model = None


def initialize_model():
    """Initialize Cellpose model (CPU-optimized)"""
    global model
    if model is None:
        logger.info("Initializing Cellpose model for CPU...")
        model = CellposeModel(
            device=torch.device("cpu"),
            pretrained_model="cpsam",  # Latest SAM-based model
            use_bfloat16=False  # Better CPU compatibility
        )
        logger.info("Model initialized successfully")
    return model


def process_image(image_bytes, diameter=30, batch_size=4):
    """
    Process image with Cellpose and calculate cell coverage

    Args:
        image_bytes: Raw image bytes
        diameter: Expected cell diameter (pixels)
        batch_size: Batch size for processing (lower = slower but less memory)

    Returns:
        dict with coverage percentage, mask count, and visualization
    """
    # Load image
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Convert to numpy array
    img_array = np.array(img)
    original_shape = img_array.shape[:2]

    logger.info(f"Processing image of size {original_shape}, diameter={diameter}")

    # Initialize model
    cellpose_model = initialize_model()

    # Run segmentation (CPU-optimized parameters)
    masks, flows, styles = cellpose_model.eval(
        img_array,
        batch_size=batch_size,  # Lower for CPU
        diameter=diameter,
        flow_threshold=0.4,
        cellprob_threshold=0.0,
        normalize=True,
        min_size=15,  # Minimum cell size
        resample=False,  # Skip resampling for speed
        augment=False  # Disable augmentation for speed
    )

    # Calculate coverage statistics
    total_pixels = masks.shape[0] * masks.shape[1]
    cell_pixels = np.sum(masks > 0)
    coverage_percent = (cell_pixels / total_pixels) * 100
    num_cells = len(np.unique(masks)) - 1  # Subtract background

    logger.info(f"Found {num_cells} cells, coverage: {coverage_percent:.2f}%")

    # Create visualization with colored masks
    mask_overlay = create_mask_overlay(img_array, masks)

    # Convert visualization to base64
    overlay_pil = Image.fromarray(mask_overlay)
    buffered = io.BytesIO()
    overlay_pil.save(buffered, format="PNG")
    overlay_base64 = base64.b64encode(buffered.getvalue()).decode()

    return {
        'coverage_percent': round(coverage_percent, 2),
        'num_cells': int(num_cells),
        'total_pixels': int(total_pixels),
        'cell_pixels': int(cell_pixels),
        'image_size': original_shape,
        'overlay_image': overlay_base64
    }


def create_mask_overlay(image, masks, alpha=0.4):
    """
    Create a colored overlay of masks on the original image

    Args:
        image: Original image (H, W, 3)
        masks: Labeled mask array (H, W)
        alpha: Transparency of overlay

    Returns:
        Overlay image as numpy array
    """
    # Generate random colors for each cell
    num_masks = masks.max()
    colors = np.random.randint(0, 255, size=(num_masks + 1, 3), dtype=np.uint8)
    colors[0] = [0, 0, 0]  # Background is black

    # Create colored mask
    colored_masks = colors[masks]

    # Blend with original image
    overlay = (image * (1 - alpha) + colored_masks * alpha).astype(np.uint8)

    return overlay


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle image upload and analysis"""
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get parameters
        diameter = int(request.form.get('diameter', 30))
        batch_size = int(request.form.get('batch_size', 4))

        # Validate parameters
        if diameter < 5 or diameter > 500:
            return jsonify({'error': 'Diameter must be between 5 and 500'}), 400

        if batch_size < 1 or batch_size > 16:
            return jsonify({'error': 'Batch size must be between 1 and 16'}), 400

        # Read image bytes
        image_bytes = file.read()

        # Process image
        result = process_image(image_bytes, diameter=diameter, batch_size=batch_size)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})


if __name__ == '__main__':
    # Initialize model on startup
    initialize_model()

    # Run app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
