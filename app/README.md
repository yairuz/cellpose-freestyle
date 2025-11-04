# 🔬 Cellpose Freestyle

An AI-powered web application that allows you to analyze cell images using **natural language queries**. Just describe what you want to know in plain English, upload your images, and let the AI agent figure out the rest!

## ✨ Features

- **Natural Language Interface**: Ask questions like "count the dead cells in this image" or "measure cell sizes"
- **AI Agent**: Uses Claude (Anthropic) to interpret your queries and translate them into cellpose operations
- **Smart Analysis**: Automatically determines the best parameters for segmentation based on your query
- **Visual Results**: Get segmented images with cell outlines overlaid on your original images
- **Comprehensive Metrics**: Cell counts, diameters, shapes, perimeters, and more
- **Multi-Image Support**: Analyze multiple images at once
- **Fallback Mode**: Works without AI API key using simple rule-based interpretation

## 🎯 Example Queries

- "Count the cells in this image"
- "Count the dead cells in this image"
- "Measure the diameter of all cells"
- "Show me the cell outlines"
- "Find only the large cells"
- "Analyze cell shape and roundness"
- "Identify overlapping cells"

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip
- (Optional) Anthropic API key for AI agent features

### Installation

1. **Navigate to the app directory:**
   ```bash
   cd app
   ```

2. **Install cellpose from parent directory:**
   ```bash
   pip install -e ..
   ```

3. **Install app dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Set up Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

   If you don't have an API key, the app will still work with a simple rule-based fallback.

### Running the App

```bash
python backend.py
```

The app will start on `http://localhost:5000`

Open your browser and navigate to: **http://localhost:5000**

## 📖 Usage

1. **Enter your query** in the text area (e.g., "Count the cells in this image")
2. **Upload one or more images** by clicking the upload area or dragging and dropping
3. **Click "Analyze Images"** and wait for results
4. **View results** including:
   - AI interpretation of your query
   - Summary statistics
   - Segmented images with cell outlines
   - Detailed metrics per image

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/JS interface for queries and image upload
│   (index.html)  │
└────────┬────────┘
         │
         │ HTTP POST /api/analyze
         ▼
┌─────────────────┐
│   Flask API     │  Receives query and images
│   (backend.py)  │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│  AI Agent       │  │  Cellpose Engine │
│  (Claude API)   │  │  Segmentation    │
└─────────────────┘  └──────────────────┘
         │                  │
         │                  │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   Results       │
         │   (JSON)        │
         └─────────────────┘
```

### Key Components

1. **Frontend** (`static/index.html`):
   - Clean, modern UI
   - Drag-and-drop image upload
   - Real-time results display
   - Example queries

2. **Backend** (`backend.py`):
   - Flask REST API
   - CellposeAgent: Interprets natural language queries
   - Image processing pipeline
   - Results compilation and visualization

3. **Agent System**:
   - Uses Claude (Anthropic) for query interpretation
   - Translates natural language to cellpose parameters
   - Determines which analyses to run
   - Provides explanations and suggestions

## 🔧 Configuration

### Cellpose Parameters

The agent automatically selects parameters based on your query, but you can customize the agent's behavior by modifying the `CellposeAgent.SYSTEM_PROMPT` in `backend.py`.

Available parameters:
- `diameter`: Expected cell diameter in pixels (default: auto-detect)
- `flow_threshold`: 0.0-1.0, higher = stricter (default: 0.4)
- `cellprob_threshold`: -6 to 6, lower = more cells detected (default: 0.0)
- `min_size`: Minimum cell size in pixels (default: 15)
- `do_3D`: Enable for 3D images (default: False)

### Supported Analyses

- **count**: Number of cells detected
- **diameter**: Cell size measurements
- **perimeter**: Cell boundary length
- **compactness**: Cell roundness (1.0 = perfect circle)
- **outlines**: Cell boundary coordinates

## 🐛 Troubleshooting

### "Model not found" error
Make sure cellpose is installed correctly:
```bash
pip install -e ..
```

### "ANTHROPIC_API_KEY not set" warning
This is normal if you don't have an API key. The app will use rule-based fallback.

### GPU not detected
Cellpose will automatically fall back to CPU. For faster processing, ensure you have:
- CUDA-compatible GPU
- PyTorch with CUDA support installed

### Images not processing
Supported formats: PNG, JPEG, TIFF
Try converting your images to PNG if you encounter issues.

## 📝 API Reference

### POST /api/analyze

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `query` (string): Natural language query
  - `images` (files): One or more image files

**Response:**
```json
{
  "query": "count the cells",
  "task": {
    "operation": "segment_and_analyze",
    "parameters": { ... },
    "analyses": ["count"],
    "explanation": "...",
    "notes": "..."
  },
  "results": [
    {
      "image_name": "cells.png",
      "cell_count": 42,
      "visualization": "base64-encoded-image",
      "diameters": { ... },
      ...
    }
  ],
  "summary": "Analyzed 1 image(s). Total cells detected: 42"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "cellpose_model_loaded": true,
  "agent_available": true
}
```

## 🤝 Contributing

This app is part of the cellpose project. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This app is part of the cellpose project and follows the same license.

## 🙏 Acknowledgments

- **Cellpose**: Developed by the Stringer Lab (Pachitariu & Stringer, 2021)
- **Claude AI**: Powered by Anthropic
- Built with Flask, NumPy, and modern web technologies

## 📚 References

- Cellpose paper: https://www.nature.com/articles/s41592-020-01018-x
- Cellpose documentation: https://cellpose.readthedocs.io/

## 💡 Tips for Best Results

1. **Be specific in your queries**: Instead of "analyze cells", try "count the cells and measure their sizes"
2. **Use clear images**: Higher quality images produce better segmentations
3. **Adjust for cell type**: Mention "dead cells" or "dim cells" if they're hard to detect
4. **Experiment with queries**: The AI agent learns from context - try different phrasings
5. **Multi-image analysis**: Upload multiple images to get aggregate statistics

---

Made with ❤️ for the cell biology community
