# Image Classification API

> Live Web Version:
> Try it online now: https://api-fenlei-production.up.railway.app/
> (Hosted on Railway — free plan; the first request may be slow after inactivity)


![Demo](demo.gif)


A simple Flask REST API for image classification using a pre-trained MobileNetV2 model (TensorFlow/Keras). It includes a modern web interface, batch image processing, and solid error handling. You can run it on Replit, locally, Docker, or Railway.

---

## Quick Start

### Try Online
- Open the live app: https://api-fenlei-production.up.railway.app/



### Local Installation
1. Clone or download the project
2. Set up requirements:
   ```bash
   cp dependencies.txt requirements.txt
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
5. Open your browser at http://localhost:5000

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

- Max file size: 16MB per image
- Max batch size: 10 images
- Supported dimensions: 32x32 to 4096x4096 px
- Supported formats: JPG, JPEG, PNG, GIF, BMP, WEBP

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
├── dependencies.txt    # Python package requirements
└── (optional) data/    # Temporary JSON storage folder if enabled (created at runtime)
```

---

## Technology & Architecture

### Backend
- Flask (Blueprint pattern)
- RESTful API with clear JSON errors
- Pillow (PIL) for image handling
- ProxyFix middleware for reverse proxy headers

### Frontend
- Bootstrap 5 (dark theme, responsive)
- Vanilla JavaScript for uploads, previews, and API calls
- Mobile-friendly UI

### Machine Learning
- TensorFlow 2.18+ and Keras
- Model: MobileNetV2 (ImageNet weights)
- Input size: 224x224 (auto-resized)
- Output: Top-K predictions with confidence scores

### File Handling
- Secure filename handling
- Validation for type, size, dimensions, and content
- In-memory processing (no persistent storage by default)

### Deployment
- Gunicorn for production
- WSGI standard
- Docker support
- Railway for quick cloud hosting (free plan supported)

---

## Data Storage (Temporary JSON) and Database Option

- By default, the app can save classification metadata temporarily to a local .json file in the repository folder (for demos/tests).
- This is not intended for production: JSON files don’t scale and may be visible if your repo is public.
- You can switch to a real database (e.g., SQLite for local development or PostgreSQL for production).

Suggested approach to use a database:
- Add and pin dependencies in requirements (for example):
  - SQLAlchemy (ORM)
  - psycopg2-binary (PostgreSQL) or use SQLite (built-in)
- Configure environment variables (examples):
  - STORAGE_BACKEND=database
  - DATABASE_URL=postgresql://user:password@host:5432/dbname
- Update the data-saving logic to write/read from the database instead of the JSON file.

If you prefer to keep JSON storage:
- Keep STORAGE_BACKEND=filesystem (or leave it unset, depending on your setup).
- The app will write a temporary .json file locally while it’s running.

---

## Model Information

- Architecture: MobileNetV2
- Trained on: ImageNet (1000 classes)
- Input: 224x224 px RGB images
- Output: Top-K predictions with confidence scores

---

## Troubleshooting

### Common Issues
1. TensorFlow import errors
   - Ensure NumPy is compatible: `pip install "numpy>=1.24.0,<2.0.0"`
   - Reinstall/upgrade TensorFlow: `pip install --upgrade tensorflow>=2.15.0`
2. Port already in use
   - Change the port in main.py
   - Kill existing process: `pkill -f "python main.py"`
3. Memory issues
   - Reduce batch size
   - Ensure enough RAM for TensorFlow
4. File uploads
   - Check file size and format
   - Verify file permissions

### Performance Tips
- The model loads once at startup (first prediction can be slower)
- Images are resized to 224x224 and processed in memory
- Use multiple Gunicorn workers under load

---

## Development Guidelines

- Use Flask Blueprints for routes
- Keep ML logic in ml_classifier.py
- Update UI in templates/ and static/
- Add validation in utils.py
- Use dependencies.txt as a template for requirements.txt
- Manage secrets via environment variables (.env for local)

Adding features:
1. New endpoints: api_routes.py
2. ML changes: ml_classifier.py
3. UI updates: templates/, static/
4. Validation: utils.py

---

## Setup & Deployment

### Local Development

Prerequisites
- Python 3.11+
- pip
- (Recommended) Virtual environment

Steps
1. Download the project
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies
   ```bash
   cp dependencies.txt requirements.txt
   pip install -r requirements.txt
   ```
4. Environment variables (optional)
   ```bash
   echo "SESSION_SECRET=your-secret-key-here" > .env
   ```
5. Run the app
   ```bash
   python main.py
   # or production:
   gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
   ```

### Docker Deployment

Create a Dockerfile:

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

- Author: Alejandro Moral Aranda
- Academic Subject: DLBDSMTP01 – Task 2: Image classification for a refund department (focus: batch processing)
- Institution: Academic project for machine learning deployment course
- Status: ✅ Complete & running (Production-ready)
- Last Updated: August 4, 2025
- Version: 1.0.0
- Preferred communication: Simple, everyday language

---

## License

This project is open source under the MIT License.