# Overview

This is an image classification API that uses a pre-trained MobileNetV2 model to classify uploaded images. The application provides a Flask-based REST API with a web interface for users to upload single images or batches of images for classification. It leverages TensorFlow and the ImageNet dataset to provide predictions with confidence scores.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Web Interface**: Single-page application using Bootstrap 5 with dark theme
- **Client-side Logic**: Vanilla JavaScript for handling file uploads, API interactions, and UI updates
- **File Preview**: Real-time image preview functionality for user feedback
- **Responsive Design**: Mobile-friendly interface with Bootstrap grid system

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