# Dual Framework Support: Flask + Streamlit

Your image classification API now supports both **Flask** and **Streamlit** frameworks with automatic fallback functionality.

## Framework Options

### 🌶️ **Flask (Primary)**
- **URL**: `http://localhost:5000`
- **Features**: Full REST API, Web Interface, JSON endpoints
- **Best for**: Production deployments, API integrations, web services

### 🎈 **Streamlit (Fallback)**  
- **URL**: `http://localhost:8501`
- **Features**: Interactive dashboard, Real-time UI, Data visualization
- **Best for**: Rapid prototyping, data science demos, internal tools

## How to Run

### **Option 1: Automatic (Recommended)**
```bash
python main.py
```
- Tries Flask first
- Falls back to Streamlit if Flask fails
- Smart framework selection

### **Option 2: Force Flask**
```bash
python main_flask.py
```
- Runs Flask only
- No fallback

### **Option 3: Force Streamlit**
```bash
# Method 1: Environment variable
FORCE_STREAMLIT=true python main.py

# Method 2: Direct launch
python run_streamlit.py

# Method 3: Streamlit CLI
streamlit run streamlit_app.py --server.port 8501
```

## Features Comparison

| Feature | Flask | Streamlit |
|---------|-------|-----------|
| **Single Image Classification** | ✅ Web Form | ✅ File Uploader |
| **Batch Processing** | ✅ Multi-file Upload | ✅ Multi-file Upload |
| **Prediction History** | ✅ JSON API + Table | ✅ Interactive Dashboard |
| **Statistics Dashboard** | ✅ Bootstrap UI | ✅ Metrics & Charts |
| **REST API Endpoints** | ✅ Full API | ❌ N/A |
| **Real-time Updates** | ❌ Manual Refresh | ✅ Auto-refresh |
| **File Download** | ✅ JSON Export | ✅ CSV Export |

## Environment Variables

Configure the launcher behavior:

```bash
# Force Streamlit mode
export FORCE_STREAMLIT=true

# Custom host/port for Flask
export HOST=0.0.0.0
export PORT=5000

# Flask environment
export FLASK_ENV=development
```

## Project Structure

```
├── main.py              # 🚀 Universal launcher (Flask → Streamlit)
├── main_flask.py        # 🌶️ Flask-only entry point
├── run_streamlit.py     # 🎈 Streamlit-only runner
├── app.py               # 🌶️ Flask application
├── streamlit_app.py     # 🎈 Streamlit application
├── app_launcher.py      # 🔧 Launcher utilities
├── ml_classifier.py     # 🧠 ML model (shared)
├── prediction_logger.py # 📊 Logging system (shared)
└── utils.py             # 🔧 Utilities (shared)
```

## Troubleshooting

### Flask Issues
```bash
# Check if port is in use
lsof -i :5000

# Kill existing Flask processes
pkill -f "flask"
pkill -f "gunicorn"
```

### Streamlit Issues
```bash
# Check Streamlit installation
pip show streamlit

# Run with verbose output
streamlit run streamlit_app.py --logger.level debug
```

### Dependencies
```bash
# Install missing packages
pip install flask streamlit tensorflow pillow

# Or using the included dependencies file
pip install -r dependencies.txt
```

## Deployment Options

### **Replit (Current Environment)**
- Click "Run" button (uses Flask by default)
- Use web preview to access the application
- Automatic port management

### **Local Development**
```bash
# Flask development server
python main.py

# Streamlit development server  
FORCE_STREAMLIT=true python main.py
```

### **Production Deployment**
```bash
# Flask with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 main_flask:app

# Streamlit standalone
streamlit run streamlit_app.py --server.port 8501
```

## Author Information

- **Author**: Alejandro Moral Aranda
- **Project**: DLBDSMTP01 – Task 2: Image classification for a refund department
- **Focus**: Batch processing with dual framework support
- **Technology**: Flask/Streamlit + TensorFlow + MobileNetV2