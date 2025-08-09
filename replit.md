# Overview

This is an image classification API that uses a pre-trained MobileNetV2 model to classify uploaded images. The application provides a Flask-based REST API with a web interface for users to upload single images or batches of images for classification. It leverages TensorFlow and the ImageNet dataset to provide predictions with confidence scores.

## Project Status
- **Status**: ✅ Complete and running with dual framework support
- **Last Updated**: August 9, 2025
- **Version**: 2.0.0
- **Current State**: Production-ready with Flask and Streamlit support
- **New Features**: Automatic framework fallback, Streamlit dashboard, Enhanced logging

# User Preferences

Preferred communication style: Simple, everyday language.

## Project Attribution
- **Author**: Alejandro Moral Aranda
- **Academic Subject**: DLBDSMTP01 – Project: From Model to Production
- **Assignment**: Task 2: Image classification for a refund department (spotlight: Batch processing)
- **Institution**: Academic project for machine learning deployment course

# System Architecture

## Frontend Architecture
- **Dual Framework Support**: Flask web interface + Streamlit dashboard
- **Flask Interface**: Single-page application using Bootstrap 5 with dark theme
- **Streamlit Interface**: Interactive dashboard with real-time updates and data visualization
- **Client-side Logic**: Vanilla JavaScript for Flask, Python widgets for Streamlit
- **File Preview**: Real-time image preview functionality in both interfaces
- **Responsive Design**: Mobile-friendly interface with Bootstrap (Flask) and Streamlit responsive components

## Backend Architecture
- **Framework**: Flask with Blueprint pattern for modular route organization
- **API Design**: RESTful endpoints following standard HTTP conventions
- **Error Handling**: Comprehensive error handling with structured JSON responses
- **File Processing**: Secure file upload handling with validation and size limits
- **Middleware**: ProxyFix for handling reverse proxy headers

## Machine Learning Architecture
- **Model**: Pre-trained MobileNetV2 from TensorFlow/Keras
- **Dataset**: ImageNet classification (1000 classes)
- **Image Processing**: PIL for image manipulation and preprocessing
- **Input Validation**: Multi-layer validation including file type, dimensions, and content verification
- **Preprocessing Pipeline**: Automatic resizing, format conversion, and normalization

## File Handling & Validation
- **Supported Formats**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Size Limits**: 16MB maximum file size, 32x32 to 4096x4096 pixel dimensions
- **Security**: Secure filename handling and file content validation
- **Memory Management**: Efficient file processing without persistent storage

## API Structure
- **Single Image Classification**: `/api/classify` endpoint for individual image processing
- **Health Check**: `/api/health` endpoint for API status monitoring
- **Error Responses**: Standardized error format with descriptive messages
- **Request Handling**: Multipart form data support for file uploads

# External Dependencies

## Machine Learning Framework
- **TensorFlow**: Deep learning framework for model execution
- **Keras**: High-level neural network API integrated with TensorFlow
- **Pre-trained Models**: MobileNetV2 with ImageNet weights

## Web Framework & Server
- **Flask**: Python web framework for API development
- **Werkzeug**: WSGI utility library for request handling and security

## Image Processing
- **Pillow (PIL)**: Python imaging library for image manipulation
- **NumPy**: Numerical computing for array operations

## Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements

## Python Standard Libraries
- **logging**: Application logging and debugging
- **io**: In-memory file handling
- **os**: Environment variable management

## Development & Deployment
- **WSGI**: Standard interface for Python web applications
- **Environment Variables**: Configuration management for secrets and settings

# Setup Instructions

## Running on Replit (Current Environment)
The application is pre-configured and ready to run:

1. **Start the Application**: Click the "Run" button or use the "Start application" workflow
2. **Access the Web Interface**: Open the web preview to interact with the application
3. **Test the API**: Use the built-in web interface or the provided PowerShell script

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

1. **Download the Project**
   ```bash
   # Download as ZIP from Replit or clone if using Git
   # Extract to your desired directory
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Copy dependencies.txt to requirements.txt
   cp dependencies.txt requirements.txt
   
   # Install packages
   pip install -r requirements.txt
   ```

4. **Environment Variables** (Optional)
   ```bash
   # Create .env file for local development
   echo "SESSION_SECRET=your-secret-key-here" > .env
   
   # For database features (optional):
   # echo "DATABASE_URL=postgresql://..." >> .env
   ```

5. **Run the Application**
   ```bash
   # Development mode
   python main.py
   
   # Production mode with Gunicorn
   gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
   ```

6. **Access the Application**
   - Open browser to `http://localhost:5000`
   - Use the web interface or API endpoints

## Testing Setup

### Web Interface Testing
1. Navigate to `http://localhost:5000`
2. Upload single images or batches
3. View classification results

### API Testing with PowerShell
```powershell
# Use the provided script
.\test_api.ps1 -ImagePath "path\to\image.jpg" -ApiUrl "http://localhost:5000"
```

### API Testing with curl
```bash
# Health check
curl http://localhost:5000/api/health

# Single image classification
curl -X POST -F "image=@path/to/image.jpg" -F "top_k=5" \
     http://localhost:5000/api/classify

# API information
curl http://localhost:5000/api/info
```

## Deployment Options

### Replit Deployment
- Use Replit's built-in deployment features
- Application is already configured for Replit hosting

### Local Server Deployment
```bash
# Using Gunicorn (recommended for production)
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app

# Using Flask development server (not for production)
python main.py
```

### Docker Deployment (Optional)
```dockerfile
# Create Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

## Troubleshooting

### Common Issues

1. **TensorFlow Import Errors**
   - Ensure NumPy version is compatible: `pip install "numpy>=1.24.0,<2.0.0"`
   - Reinstall TensorFlow: `pip install --upgrade tensorflow>=2.15.0`

2. **Port Already in Use**
   - Change port in main.py or use different port
   - Kill existing processes: `pkill -f "python main.py"`

3. **Memory Issues**
   - Reduce batch size for image processing
   - Ensure sufficient RAM for TensorFlow model loading

4. **File Upload Issues**
   - Check file size limits (16MB max)
   - Verify image format is supported
   - Ensure proper file permissions

### Performance Optimization

1. **Model Loading**
   - Model is loaded once at startup and cached
   - First prediction may take longer due to model initialization

2. **Image Processing**
   - Images are automatically resized to 224x224 for model input
   - Large images are processed in memory without disk storage

3. **Concurrent Requests**
   - Use multiple Gunicorn workers for production
   - Consider implementing request queuing for high load

## Development Guidelines

### Code Structure
- Follow Flask Blueprint pattern for route organization
- Separate ML logic in dedicated modules
- Use comprehensive error handling and validation

### Adding New Features
1. **New Endpoints**: Add to `api_routes.py`
2. **ML Models**: Extend `ml_classifier.py`
3. **UI Changes**: Modify `templates/` and `static/` files
4. **Validation**: Update `utils.py` helper functions

### Dependencies Management
- Use `dependencies.txt` as template for `requirements.txt`
- Pin major versions for stability
- Test compatibility after updates