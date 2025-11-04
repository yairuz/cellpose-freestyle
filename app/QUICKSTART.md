# Cellpose Freestyle - Quick Start Guide

Get up and running with Cellpose Freestyle in under 5 minutes!

## 🚀 Three Ways to Run

### Option 1: Automated Script (Recommended)

The easiest way to get started:

```bash
cd app
./run.sh
```

This script will:
- ✅ Check Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Check for API key (optional)
- ✅ Launch the server

**Then open:** http://localhost:5000

### Option 2: Docker (For Production)

If you have Docker installed:

```bash
cd app

# Set your API key (optional)
export ANTHROPIC_API_KEY='your-key-here'

# Build and run
docker-compose up
```

**Then open:** http://localhost:5000

### Option 3: Manual Setup

For development or custom setups:

```bash
cd app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ..
pip install -r requirements.txt

# (Optional) Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run
python backend.py
```

**Then open:** http://localhost:5000

## 📸 Try it Out

### 1. Generate Sample Images

Create test images to experiment with:

```bash
python generate_samples.py
```

This creates 4 sample images in `sample_images/`:
- `basic_cells.png` - Standard cell image
- `dense_cells.png` - Crowded/overlapping cells
- `dim_cells.png` - Low-intensity "dead" cells
- `varied_cells.png` - Mixed small and large cells

### 2. Run Your First Analysis

1. Open http://localhost:5000
2. Enter a query (try one below)
3. Upload an image from `sample_images/`
4. Click "Analyze Images"

### Example Queries to Try

**Basic Counting:**
```
Count the cells in this image
```

**Specific Detection:**
```
Count the dead cells in this image
```
(Use with `dim_cells.png`)

**Measurements:**
```
Measure the diameter of all cells
```

**Filtering:**
```
Find only the large cells
```
(Use with `varied_cells.png`)

**Shape Analysis:**
```
Analyze cell shape and roundness
```

**Dense Regions:**
```
Count cells in crowded areas
```
(Use with `dense_cells.png`)

## 🔑 API Key Setup (Optional)

For the best AI interpretation, set up an Anthropic API key:

### Get an API Key

1. Sign up at https://console.anthropic.com/
2. Navigate to API Keys
3. Create a new key

### Set the Key

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY='your-key-here'
```

**Permanent Setup:**

Add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Without API Key:**
The app still works! It uses rule-based interpretation instead.

## 📊 Understanding Results

After analysis, you'll see:

1. **Task Interpretation** - How the AI understood your query
2. **Summary** - Quick overview of findings
3. **Visualizations** - Your images with cell outlines overlaid
4. **Metrics** - Detailed measurements:
   - Cell count
   - Diameters (mean, range)
   - Roundness/compactness
   - Perimeters

## 🎯 Tips for Best Results

### Image Quality
- ✅ Use clear, well-focused images
- ✅ Higher resolution = better segmentation
- ✅ Consistent lighting helps

### Query Phrasing
- ✅ Be specific: "count the cells and measure sizes"
- ✅ Mention cell characteristics: "dead cells", "large cells"
- ✅ Ask for what you need: measurements, shapes, counts

### Special Cases

**Dim/Dead Cells:**
```
Count the dead cells
```
→ Uses lower threshold to detect faint cells

**Large Cells Only:**
```
Find only the large cells
```
→ Filters by minimum size

**3D Images:**
```
Segment this 3D image stack
```
→ Enables 3D processing

## 🐛 Troubleshooting

### Port Already in Use

If port 5000 is taken, edit `backend.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Changed port
```

### Dependencies Missing

```bash
pip install -r requirements.txt --force-reinstall
```

### Cellpose Not Found

```bash
cd app
pip install -e ..  # Install from parent directory
```

### GPU Not Detected

Cellpose automatically falls back to CPU. For GPU support:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Image Won't Upload

Supported formats: PNG, JPEG, TIFF
Maximum size: Limited by Flask settings (can be adjusted)

## 📚 Next Steps

- **Read the full docs:** [README.md](README.md)
- **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Programmatic usage:** [example_usage.py](example_usage.py)
- **Main cellpose docs:** https://cellpose.readthedocs.io/

## 💡 Common Use Cases

### Research Lab Workflow

1. Capture microscopy images
2. Upload to Cellpose Freestyle
3. Ask: "Count cells and measure sizes"
4. Export results for analysis

### High-Throughput Screening

1. Batch upload multiple images
2. Ask: "Count live and dead cells"
3. Compare across conditions
4. Generate summary statistics

### Teaching/Education

1. Generate sample images
2. Demonstrate cell segmentation
3. Show effect of parameters
4. Interactive learning

---

**Ready to analyze cells?** → http://localhost:5000

**Questions?** Open an issue on GitHub or check the docs!
