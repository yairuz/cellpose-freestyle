# Quick Start Guide

## Fastest Way to Run (3 commands)

```bash
cd webapp
./start.sh
# Visit http://localhost:5000
```

## Using Docker (Alternative)

```bash
cd webapp
docker-compose up
# Visit http://localhost:5000
```

## Manual Setup

```bash
cd webapp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

## First Use

1. The first request will download the Cellpose model (~500MB) automatically
2. This is a one-time download, cached in `~/.cellpose/models/`
3. Upload a microscopy image (PNG, JPG, or TIFF)
4. Adjust cell diameter if needed (default: 30 pixels)
5. Click "Analyze Image" and wait 30-60 seconds
6. View results: coverage %, cell count, and visual overlay

## Performance Tips

- **Smaller images** (512x512): ~20-30 seconds
- **Larger images** (1024x1024): ~45-60 seconds
- Reduce batch size (1-2) if you run out of memory
- First request is slower due to model loading (~10-20s extra)

## Troubleshooting

**Problem**: Out of memory
- **Solution**: Reduce batch size to 1, or resize image to 512x512

**Problem**: Processing too slow
- **Solution**: See deployment options in README.md for GPU acceleration

**Problem**: Model download fails
- **Solution**: Check internet connection and disk space (~1GB needed)
