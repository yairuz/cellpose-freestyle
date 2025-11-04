"""
Cellpose Freestyle App - Backend API
Accepts free-form queries and images, uses an AI agent to interpret requests,
and executes cellpose operations accordingly.
"""

import os
import json
import base64
from io import BytesIO
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
from PIL import Image
import anthropic

# Import cellpose
from cellpose import models, io, utils

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize cellpose model (do this once at startup)
print("Loading Cellpose model...")
cellpose_model = models.CellposeModel(gpu=True, pretrained_model="cpsam")
print("Model loaded successfully!")

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY not set. Agent features will not work.")
    anthropic_client = None
else:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


class CellposeAgent:
    """Agent that interprets free-form queries and translates them to cellpose operations."""

    SYSTEM_PROMPT = """You are a cellpose expert agent. Your job is to interpret user queries about cell image analysis and translate them into structured cellpose operations.

Cellpose can perform the following operations:
- Segment cells/nuclei in images
- Count cells
- Measure cell sizes (diameter, area)
- Measure cell shape properties (perimeter, compactness/roundness)
- Extract cell outlines
- Identify touching/overlapping cells
- Filter cells by size
- 3D segmentation (if the image is 3D)

Available parameters:
- diameter: Expected cell diameter in pixels (default: auto-detect)
- flow_threshold: 0.0-1.0 (higher = stricter, default 0.4)
- cellprob_threshold: -6 to 6 (lower = more cells detected, default 0.0)
- min_size: Minimum cell size in pixels (default 15)
- do_3D: True for 3D images (default False)

Common query patterns:
- "count cells" → segment and count
- "measure cell sizes" → segment and measure diameters
- "dead cells" → may need lower cellprob_threshold to catch dim cells
- "large cells only" → use higher min_size
- "overlapping cells" → check if masks are touching

Your response MUST be valid JSON with this structure:
{
  "operation": "segment_and_analyze",
  "parameters": {
    "diameter": null or number,
    "flow_threshold": number,
    "cellprob_threshold": number,
    "min_size": number,
    "do_3D": boolean
  },
  "analyses": ["count", "diameter", "perimeter", "compactness", "outlines"],
  "explanation": "Brief explanation of what will be done",
  "notes": "Any important notes or suggestions for the user"
}

The "analyses" field should include which measurements to return based on the query."""

    def __init__(self, client):
        self.client = client

    def interpret_query(self, query: str) -> dict:
        """Interpret a free-form query and return structured cellpose task."""
        if not self.client:
            # Fallback if no API key
            return self._fallback_interpretation(query)

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Interpret this query: {query}"
                    }
                ]
            )

            response_text = message.content[0].text
            # Parse JSON from response
            return json.loads(response_text)

        except Exception as e:
            print(f"Error in agent interpretation: {e}")
            return self._fallback_interpretation(query)

    def _fallback_interpretation(self, query: str) -> dict:
        """Simple rule-based fallback if no LLM available."""
        query_lower = query.lower()

        # Default parameters
        task = {
            "operation": "segment_and_analyze",
            "parameters": {
                "diameter": None,
                "flow_threshold": 0.4,
                "cellprob_threshold": 0.0,
                "min_size": 15,
                "do_3D": False
            },
            "analyses": ["count"],
            "explanation": "Performing basic cell segmentation and counting",
            "notes": "Using default parameters. Set ANTHROPIC_API_KEY for smarter interpretation."
        }

        # Adjust based on keywords
        if "dead" in query_lower or "dim" in query_lower:
            task["parameters"]["cellprob_threshold"] = -2.0
            task["notes"] = "Using lower threshold to detect dim/dead cells"

        if "large" in query_lower:
            task["parameters"]["min_size"] = 50
            task["notes"] = "Filtering for larger cells only"

        if "size" in query_lower or "diameter" in query_lower or "area" in query_lower:
            task["analyses"].extend(["diameter"])

        if "shape" in query_lower or "round" in query_lower or "compact" in query_lower:
            task["analyses"].extend(["compactness"])

        if "outline" in query_lower or "boundary" in query_lower or "edge" in query_lower:
            task["analyses"].append("outlines")

        if "perimeter" in query_lower:
            task["analyses"].append("perimeter")

        # Remove duplicates
        task["analyses"] = list(set(task["analyses"]))

        return task


# Initialize agent
agent = CellposeAgent(anthropic_client)


def process_image(image_data: bytes, task: dict) -> dict:
    """Process an image with cellpose based on the task specification."""

    # Load image
    image = np.array(Image.open(BytesIO(image_data)))

    # Run segmentation
    params = task["parameters"]
    masks, flows, styles = cellpose_model.eval(
        image,
        diameter=params.get("diameter"),
        flow_threshold=params.get("flow_threshold", 0.4),
        cellprob_threshold=params.get("cellprob_threshold", 0.0),
        min_size=params.get("min_size", 15),
        do_3D=params.get("do_3D", False),
        batch_size=8
    )

    # Perform requested analyses
    results = {}
    analyses = task.get("analyses", ["count"])

    if "count" in analyses:
        results["cell_count"] = int(masks.max())

    if "diameter" in analyses:
        diameters = utils.diameters(masks)
        results["diameters"] = {
            "mean": float(np.mean(diameters)) if len(diameters) > 0 else 0,
            "median": float(np.median(diameters)) if len(diameters) > 0 else 0,
            "std": float(np.std(diameters)) if len(diameters) > 0 else 0,
            "min": float(np.min(diameters)) if len(diameters) > 0 else 0,
            "max": float(np.max(diameters)) if len(diameters) > 0 else 0,
            "all_values": [float(d) for d in diameters]
        }

    if "perimeter" in analyses:
        perimeters = utils.get_mask_perimeters(masks)
        results["perimeters"] = {
            "mean": float(np.mean(perimeters)),
            "all_values": [float(p) for p in perimeters]
        }

    if "compactness" in analyses:
        compactness = utils.get_mask_compactness(masks)
        results["compactness"] = {
            "mean": float(np.mean(compactness)),
            "all_values": [float(c) for c in compactness]
        }

    if "outlines" in analyses:
        outlines = utils.outlines_list(masks)
        results["outlines_count"] = len(outlines)

    # Generate visualization
    outlines = utils.masks_to_outlines(masks)

    # Create overlay image
    if len(image.shape) == 2:  # Grayscale
        overlay = np.stack([image, image, image], axis=-1)
    else:
        overlay = image.copy()

    # Ensure overlay is uint8
    if overlay.dtype != np.uint8:
        overlay = ((overlay - overlay.min()) / (overlay.max() - overlay.min()) * 255).astype(np.uint8)

    # Draw outlines in red
    overlay[outlines > 0] = [255, 0, 0]

    # Convert to base64 for sending to frontend
    overlay_pil = Image.fromarray(overlay)
    buffer = BytesIO()
    overlay_pil.save(buffer, format="PNG")
    overlay_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    results["visualization"] = overlay_base64

    return results


@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory('static', 'index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main API endpoint.
    Accepts: query (text) and images (files)
    Returns: analysis results and visualizations
    """
    try:
        # Get query
        query = request.form.get('query', '')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Get images
        if 'images' not in request.files:
            return jsonify({"error": "No images provided"}), 400

        images = request.files.getlist('images')
        if not images:
            return jsonify({"error": "No images provided"}), 400

        # Step 1: Interpret query with agent
        print(f"Interpreting query: {query}")
        task = agent.interpret_query(query)
        print(f"Task interpretation: {json.dumps(task, indent=2)}")

        # Step 2: Process each image
        all_results = []
        for idx, image_file in enumerate(images):
            image_data = image_file.read()
            print(f"Processing image {idx + 1}/{len(images)}...")

            result = process_image(image_data, task)
            result["image_name"] = image_file.filename
            all_results.append(result)

        # Step 3: Compile response
        response = {
            "query": query,
            "task": task,
            "results": all_results,
            "summary": generate_summary(all_results, task)
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error in /api/analyze: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def generate_summary(results: list, task: dict) -> str:
    """Generate a human-readable summary of results."""
    summary_parts = []

    num_images = len(results)
    summary_parts.append(f"Analyzed {num_images} image(s).")

    # Total cell count
    if any("cell_count" in r for r in results):
        total_cells = sum(r.get("cell_count", 0) for r in results)
        summary_parts.append(f"Total cells detected: {total_cells}")

        if num_images > 1:
            per_image = [r.get("cell_count", 0) for r in results]
            summary_parts.append(f"Per image: {', '.join(str(c) for c in per_image)}")

    # Diameter statistics
    if any("diameters" in r for r in results):
        all_diameters = []
        for r in results:
            if "diameters" in r:
                all_diameters.extend(r["diameters"]["all_values"])

        if all_diameters:
            mean_diameter = np.mean(all_diameters)
            summary_parts.append(f"Average cell diameter: {mean_diameter:.1f} pixels")

    # Compactness
    if any("compactness" in r for r in results):
        all_compactness = []
        for r in results:
            if "compactness" in r:
                all_compactness.extend(r["compactness"]["all_values"])

        if all_compactness:
            mean_compactness = np.mean(all_compactness)
            summary_parts.append(f"Average cell roundness: {mean_compactness:.2f} (1.0 = perfect circle)")

    return " ".join(summary_parts)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "cellpose_model_loaded": cellpose_model is not None,
        "agent_available": anthropic_client is not None
    })


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)

    print("\n" + "="*60)
    print("Cellpose Freestyle App")
    print("="*60)
    print(f"Agent available: {anthropic_client is not None}")
    print(f"To enable agent features, set ANTHROPIC_API_KEY environment variable")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
