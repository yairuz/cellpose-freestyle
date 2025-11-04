# Cellpose Cell Coverage Analyzer Web App

A web application that analyzes cell coverage in microscopy images using Cellpose. Users can upload an image, and the app will segment cells and calculate the percentage of the image covered by cells.

## Features

- Simple drag-and-drop interface
- CPU-optimized processing (handles images in ~30-60 seconds)
- Visual overlay of detected cells
- Coverage statistics (percentage, cell count, pixel counts)
- Adjustable parameters (cell diameter, batch size)

## Running Locally

### Prerequisites

- Python 3.8 or higher
- 4GB+ RAM recommended
- CPU with AVX2 support recommended for optimal performance

### Installation

1. Navigate to the webapp directory:
```bash
cd webapp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload an image and click "Analyze Image"

## Performance Notes

### CPU Performance
- **Image size**: 512x512 pixels typically processes in 20-40 seconds on modern CPUs
- **Larger images** (1024x1024+): May take 45-60 seconds
- **Batch size**: Lower values (1-4) use less memory but are slower
- **Model loading**: First request takes ~10-20 seconds to load the model

### Optimization Tips
- Reduce batch size if running out of memory
- Use smaller cell diameter values if processing is too slow
- Resize large images before uploading (e.g., max 1024x1024)

## Deployment Options

### Option 1: Cloud VM (Recommended for CPU)

Deploy on a cloud VM with sufficient CPU resources:

**Digital Ocean / Linode / AWS EC2**
- Instance: 4 vCPU, 8GB RAM (e.g., AWS t3.xlarge)
- Cost: ~$0.15/hour on-demand, or $60-100/month reserved
- Setup time: 15 minutes

**Deployment steps:**
```bash
# 1. SSH into your VM
ssh user@your-server-ip

# 2. Clone/upload your code
git clone <your-repo>
cd webapp

# 3. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run with Gunicorn (production server)
gunicorn -w 2 -b 0.0.0.0:5000 --timeout 120 app:app
```

**Nginx reverse proxy (optional):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_read_timeout 120s;
        client_max_body_size 20M;
    }
}
```

### Option 2: Docker Container

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

Build and run:
```bash
docker build -t cellpose-webapp .
docker run -p 5000:5000 cellpose-webapp
```

### Option 3: Render.com (Easy, Free Tier Available)

1. Push your code to GitHub
2. Create new Web Service on [Render.com](https://render.com)
3. Connect your repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 app:app`
   - **Instance Type**: Standard (4GB+ RAM)

**Free tier limitations**: Spins down after inactivity, limited to 750 hours/month

### Option 4: Hugging Face Spaces

For easy sharing with the community:

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose "Gradio" or convert to Gradio interface
3. Upload your code
4. Automatic deployment with free GPU access (limited hours)

**Gradio conversion** (simpler alternative to Flask):
```python
import gradio as gr
from cellpose.models import CellposeModel
import numpy as np

model = CellposeModel(device="cpu", pretrained_model="cpsam")

def analyze_cells(image, diameter=30):
    masks, _, _ = model.eval(image, diameter=diameter)
    coverage = (masks > 0).sum() / masks.size * 100
    return f"Coverage: {coverage:.2f}%", masks

demo = gr.Interface(
    fn=analyze_cells,
    inputs=[gr.Image(), gr.Slider(5, 100, value=30)],
    outputs=[gr.Text(), gr.Image()],
    title="Cell Coverage Analyzer"
)

demo.launch()
```

### Option 5: GPU Acceleration (If CPU is Too Slow)

If CPU performance is insufficient, deploy with GPU support:

**Cloud providers with GPU:**
- **AWS EC2**: g4dn.xlarge (~$0.50/hour) - NVIDIA T4 GPU
- **Google Cloud**: n1-standard-4 + T4 GPU (~$0.50/hour)
- **Paperspace**: GPU instances starting at $0.45/hour
- **Lambda Labs**: RTX 6000 starting at $0.50/hour

**Code changes for GPU:**
```python
# In app.py, change initialize_model():
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CellposeModel(
    device=device,
    pretrained_model="cpsam",
    gpu=True if device.type == "cuda" else False
)
```

**Performance with GPU:**
- 512x512 image: ~2-5 seconds
- 1024x1024 image: ~5-10 seconds
- Much better for real-time usage

### Recommended Deployment Strategy

For **personal/small team use**:
- Start with **Render.com** (easiest, free tier)
- Upgrade to paid plan ($7-20/month) if needed

For **public/production use**:
- **CPU**: AWS/Digital Ocean VM with 4+ vCPUs (~$60-100/month)
- **GPU**: AWS g4dn.xlarge on-demand for burst traffic
- Use **Docker** for consistent deployment
- Add caching for frequently analyzed images
- Consider queueing system (Celery + Redis) for multiple users

For **research/demo**:
- **Hugging Face Spaces** with Gradio (free, easy to share)

## API Endpoints

### POST /analyze
Analyzes an uploaded image.

**Parameters:**
- `image`: Image file (multipart/form-data)
- `diameter`: Cell diameter in pixels (default: 30)
- `batch_size`: Processing batch size (default: 4)

**Response:**
```json
{
  "coverage_percent": 45.23,
  "num_cells": 127,
  "total_pixels": 262144,
  "cell_pixels": 118572,
  "image_size": [512, 512],
  "overlay_image": "base64_encoded_image..."
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## Troubleshooting

### Out of Memory Errors
- Reduce `batch_size` parameter to 1 or 2
- Resize images to smaller dimensions before upload
- Use a machine with more RAM (8GB+ recommended)

### Slow Processing
- Ensure CPU has AVX2 support
- Try reducing image resolution
- Consider GPU deployment for real-time performance

### Model Download Issues
- First run downloads ~500MB model from HuggingFace
- Ensure internet connection and sufficient disk space
- Model cached in `~/.cellpose/models/`

## License

This application uses Cellpose, which is licensed under BSD 3-Clause License.
