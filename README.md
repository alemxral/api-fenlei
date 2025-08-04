# Image Classification API

A Flask REST API with integrated machine learning image classification using pre-trained MobileNetV2 model from TensorFlow/Keras.

## Features

- **Single Image Classification**: Upload and classify individual images
- **Batch Classification**: Process up to 10 images simultaneously
- **Web Interface**: Beautiful Bootstrap-based UI for easy interaction
- **REST API**: Well-documented endpoints for programmatic access
- **Multiple Formats**: Supports JPG, PNG, GIF, BMP, WEBP images
- **Confidence Scores**: Returns top predictions with confidence percentages
- **Error Handling**: Comprehensive validation and error responses

## Quick Start

### On Replit
The application is already configured and running. Just click the "Run" button!

### Local Installation

1. **Clone or download the project**
2. **Create requirements.txt** (copy from dependencies.txt):
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

5. **Open your browser** to `http://localhost:5000`

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

## File Limits

- **Maximum file size**: 16MB per image
- **Maximum batch size**: 10 images
- **Supported dimensions**: 32x32 to 4096x4096 pixels
- **Supported formats**: JPG, JPEG, PNG, GIF, BMP, WEBP

## Testing with PowerShell

Use the included PowerShell script to test the API:

```powershell
.\test_api.ps1 -ImagePath "path\to\image.jpg" -ApiUrl "http://localhost:5000"
```

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

## Technology Stack

- **Backend**: Flask, Python 3.11
- **ML Framework**: TensorFlow 2.18+, Keras
- **Model**: MobileNetV2 (ImageNet weights)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Image Processing**: Pillow (PIL)
- **Server**: Gunicorn

## Model Information

- **Architecture**: MobileNetV2
- **Training Dataset**: ImageNet (1000 classes)
- **Input Size**: 224x224 pixels
- **Output**: Top-K predictions with confidence scores

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

## Error Handling

The API provides detailed error messages for:
- Invalid file formats
- File size violations
- Corrupted images
- Server errors
- Missing parameters

## Development

To modify or extend the application:

1. **Add new endpoints** in `api_routes.py`
2. **Modify ML logic** in `ml_classifier.py`
3. **Update UI** in `templates/index.html` and `static/`
4. **Add validation** in `utils.py`

## License

This project is open source and available under the MIT License.