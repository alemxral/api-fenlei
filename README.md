# Image Classification API

> **Live Web Version:**
> Try it online now: [https://api-fenlei-production.up.railway.app/](https://api-fenlei-production.up.railway.app/)
> *(Hosted on Railway – free plan)*

![Web Interface Screenshot](screenshot.png)

A simple Flask REST API for image classification using a pre-trained MobileNetV2 model (TensorFlow/Keras). Includes a modern web interface, batch image processing, and robust error handling. Designed for easy deployment on Replit, local servers, Docker, or Railway.

---

## Quick Start

### Try Online
- Visit the live server: [https://api-fenlei-production.up.railway.app/](https://api-fenlei-production.up.railway.app/)

### On Replit
- The app is pre-configured and running; just hit **Run**!

### Local Installation

1. **Clone or download the project**
2. **Set up requirements**:
   ```bash
   cp dependencies.txt requirements.txt
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```
5. **Open your browser** at [http://localhost:5000](http://localhost:5000)

---

## API Endpoints

### Single Image Classification
```
POST /api/classify
Content-Type: multipart/form-data
Body: image=<file>&top_k=5
```

### Batch Classification
```
POST /api/classify/batch
Content-Type: multipart/form-data
Body: images=<files>&top_k=5
```

### Health Check
```
GET /api/health
```

### API Information
```
GET /api/info
```

---

## File & Usage Limits

- **Max file size**: 16MB/image
- **Max batch size**: 10 images
- **Supported dimensions**: 32x32 to 4096x4096 px
- **Formats**: JPG, JPEG, PNG, GIF, BMP, WEBP

---

## Example Response

```json
{
  "status": "success",
  "filename": "cat.jpg",
  "predictions": [
    {
      "class_id": "n02123045",
      "class_name": "tabby_cat",
      "confidence": 0.8532,
      "confidence_percentage": "85.32%"
    },
    {
      "class_id": "n02123159",
      "class_name": "tiger_cat",
      "confidence": 0.1243,
      "confidence_percentage": "12.43%"
    }
  ],
  "total_predictions": 5
}
```

---

## Testing

### PowerShell
```powershell
.\test_api.ps1 -ImagePath "path\to\image.jpg" -ApiUrl "http://localhost:5000"
```

### curl
```bash
# Health check
curl http://localhost:5000/api/health

# Single image classification
curl -X POST -F "image=@path/to/image.jpg" -F "top_k=5" \
     http://localhost:5000/api/classify

# API information
curl http://localhost:5000/api/info
```

---

## Project Structure

```
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── ml_classifier.py    # TensorFlow/Keras ML model handler
├── api_routes.py       # REST API endpoints
├── utils.py            # Helper functions and validation
├── templates/
│   └── index.html      # Web interface
├── static/
│   ├── css/style.css   # Custom styles
│   └── js/app.js       # Frontend JavaScript
├── test_api.ps1        # PowerShell testing script
└── dependencies.txt    # Python package requirements
```

---

## Technology & Architecture

### Backend
- **Flask** (Blueprint pattern)
- **RESTful API** with clear error responses
- **Image Processing**: Pillow (PIL)
- **Model**: MobileNetV2 (ImageNet weights), loaded/cached at startup
- **ProxyFix** middleware for reverse proxy headers

### Frontend
- **Bootstrap 5** (dark theme, responsive)
- **Vanilla JavaScript** (file upload, live preview, API calls)
- **Mobile-friendly** design

### File Handling
- Secure filename checks
- Multi-layer validation (file type, size, dimensions, content)
- No persistent storage; all processing in-memory

### Machine Learning
- **TensorFlow 2.18+**, **Keras**
- **Input size**: 224x224 px (auto-resized)
- **Output**: Top-K predictions with confidence scores

### Deployment
- **Gunicorn** for production server
- **WSGI** standard interface
- **Docker** support (see below)
- **Railway** for free cloud hosting

---

## Model Information

- **Architecture**: MobileNetV2
- **Trained on**: ImageNet (1000 classes)
- **Input**: 224x224 px RGB images
- **Output**: Top-K predictions, confidence scores

---

## Troubleshooting

### Common Issues
1. **TensorFlow errors**:
   - Ensure NumPy version is compatible: `pip install "numpy>=1.24.0,<2.0.0"`
   - Upgrade TensorFlow: `pip install --upgrade tensorflow>=2.15.0`
2. **Port in use**:
   - Change port in `main.py`
   - Kill processes: `pkill -f "python main.py"`
3. **Memory problems**:
   - Lower batch size
   - Make sure your machine has enough RAM
4. **File upload issues**:
   - Check file size and format
   - Verify permissions

### Performance Tips
- Model loads/caches at startup (first prediction may be slower)
- Large images resized automatically, processed in memory
- Use multiple Gunicorn workers for heavy load

---

## Development Guidelines

- Organize routes with Flask Blueprints
- Keep ML logic in `ml_classifier.py`
- UI updates in `templates/` & `static/`
- Add validation in `utils.py`
- Pin major package versions in `dependencies.txt`
- Use `.env` for secrets/config (see below)

### Adding Features
1. **Endpoints**: `api_routes.py`
2. **ML changes**: `ml_classifier.py`
3. **UI**: `templates/`, `static/`
4. **Validation**: `utils.py`

---

## Setup & Deployment

### Local Development

#### Prerequisites
- Python 3.11+
- pip (Python package manager)
- (Recommended) Virtual environment

#### Steps

1. **Download the project**
2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   cp dependencies.txt requirements.txt
   pip install -r requirements.txt
   ```
4. **Environment variables** (optional, for secrets/config)
   ```bash
   echo "SESSION_SECRET=your-secret-key-here" > .env
   ```
5. **Run the app**
   ```bash
   python main.py
   # Production (recommended):
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

---

## Attribution & Info

- **Author**: Alejandro Moral Aranda
- **Institution**: Academic project for machine learning deployment course
- **Course/Subject**: DLBDSMTP01 – Task 2: Batch image classification for refund department
- **Status**: ✅ Complete & running (Production-ready)
- **Last updated**: August 4, 2025
- **Version**: 1.0.0
- **Preferred communication**: Simple, everyday language

---

## License

This project is open source under the MIT License.
