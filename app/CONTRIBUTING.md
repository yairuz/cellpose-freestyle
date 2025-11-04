# Contributing to Cellpose Freestyle

Thank you for your interest in contributing to Cellpose Freestyle! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- (Optional) Docker for containerized development
- (Optional) Anthropic API key for AI features

### Quick Setup

1. **Clone and setup:**
   ```bash
   cd app
   ./run.sh  # This will setup everything automatically
   ```

   Or manually:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -e ..
   pip install -r requirements.txt
   ```

2. **Generate sample images for testing:**
   ```bash
   python generate_samples.py
   ```

3. **Run the development server:**
   ```bash
   python backend.py
   ```

## Project Structure

```
app/
├── backend.py              # Flask API server
│   ├── CellposeAgent       # AI query interpreter
│   ├── process_image()     # Image processing pipeline
│   └── API endpoints       # /api/analyze, /health
├── static/
│   └── index.html          # Frontend UI
├── requirements.txt        # Python dependencies
├── run.sh                  # Launcher script
├── Dockerfile              # Container image
├── docker-compose.yml      # Container orchestration
├── generate_samples.py     # Sample image generator
└── example_usage.py        # Programmatic examples
```

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
  - Use 4 spaces for indentation
  - Maximum line length: 88 characters (Black compatible)
  - Use type hints where applicable

- **JavaScript**: Use ES6+ features
  - Use `const` and `let` (not `var`)
  - Use async/await for promises
  - Keep functions small and focused

- **HTML/CSS**:
  - Use semantic HTML5 elements
  - Mobile-first responsive design
  - Keep styling modular

### Testing

Before submitting a PR, test:

1. **Backend functionality:**
   ```bash
   # Test imports
   python -c "import backend; print('OK')"

   # Test with sample images
   python generate_samples.py
   python backend.py &
   # Upload samples via UI
   ```

2. **Agent interpretation:**
   ```bash
   python example_usage.py
   ```

3. **Different scenarios:**
   - With ANTHROPIC_API_KEY set
   - Without API key (fallback mode)
   - Multiple images
   - Various query types

### Adding Features

#### Adding New Cellpose Operations

1. **Update `CellposeAgent.SYSTEM_PROMPT`** in `backend.py`:
   ```python
   Available operations:
   - segment cells/nuclei
   - ...
   - your_new_operation  # Add description
   ```

2. **Add analysis in `process_image()`**:
   ```python
   if "your_analysis" in analyses:
       result = utils.your_function(masks)
       results["your_analysis"] = result
   ```

3. **Update frontend** to display results:
   ```javascript
   ${result.your_analysis ? `
       <div class="metric">
           <div class="metric-label">Your Metric</div>
           <div class="metric-value">${result.your_analysis}</div>
       </div>
   ` : ''}
   ```

#### Adding New Query Patterns

1. **Update agent prompt** with examples
2. **Add fallback logic** in `_fallback_interpretation()`
3. **Test with various query phrasings**

#### UI Improvements

1. **Edit `static/index.html`**
2. **Test responsive behavior** (mobile, tablet, desktop)
3. **Ensure accessibility** (ARIA labels, keyboard navigation)

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear commits:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

3. **Test thoroughly:**
   - Run existing functionality
   - Test new features
   - Check edge cases

4. **Update documentation:**
   - Update README if needed
   - Add docstrings to new functions
   - Update CONTRIBUTING.md for new patterns

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines

Use conventional commits format:

```
type(scope): brief description

Detailed explanation if needed

Examples:
- feat(agent): add support for 3D image queries
- fix(ui): correct file preview for large images
- docs(readme): update installation instructions
- refactor(backend): simplify image processing pipeline
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance tasks

## Common Development Tasks

### Adding a New Analysis Type

Example: Adding cell area measurement

1. **Backend** (`backend.py`):
   ```python
   if "area" in analyses:
       areas = []
       for cell_id in range(1, masks.max() + 1):
           area = np.sum(masks == cell_id)
           areas.append(area)

       results["areas"] = {
           "mean": float(np.mean(areas)),
           "all_values": [float(a) for a in areas]
       }
   ```

2. **Agent prompt**:
   ```python
   - Measure cell areas → analyses: ["count", "area"]
   ```

3. **Frontend**:
   ```javascript
   ${result.areas ? `
       <div class="metric">
           <div class="metric-label">Mean Area</div>
           <div class="metric-value">${result.areas.mean.toFixed(1)} px²</div>
       </div>
   ` : ''}
   ```

### Debugging

1. **Backend debugging:**
   ```bash
   # Enable Flask debug mode (already on in backend.py)
   # Check console output for errors

   # Test specific functions
   python
   >>> from backend import CellposeAgent
   >>> agent = CellposeAgent(None)
   >>> agent.interpret_query("count cells")
   ```

2. **Frontend debugging:**
   ```javascript
   // Add console.log in JavaScript
   console.log('Response:', data);

   // Check browser Network tab for API calls
   // Check browser Console for errors
   ```

3. **Agent debugging:**
   ```python
   # Print agent responses
   print(f"Task interpretation: {json.dumps(task, indent=2)}")
   ```

## Docker Development

### Build and run with Docker:

```bash
# Build image
docker-compose build

# Run container
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Development with Docker:

The docker-compose.yml includes volume mounts for live development:
```yaml
volumes:
  - ./backend.py:/app/backend.py
  - ./static:/app/static
```

Changes to these files will be reflected immediately (may need to restart Flask).

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: For questions and ideas
- **Documentation**: Read the main README.md

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the problem, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Happy coding! 🚀
