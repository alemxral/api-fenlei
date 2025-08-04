from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging
from ml_classifier import classifier
from utils import validate_image_file, allowed_file

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/classify', methods=['POST'])
def classify_single_image():
    """
    Classify a single image
    
    Expected request: multipart/form-data with 'image' file field
    Optional query parameter: top_k (default: 5)
    """
    try:
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image provided',
                'message': 'Please provide an image file in the "image" field'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file format',
                'message': 'Please upload a valid image file (JPG, JPEG, PNG, GIF, BMP, WEBP)'
            }), 400
        
        # Validate file content
        try:
            validate_image_file(file)
        except ValueError as e:
            return jsonify({
                'error': 'Invalid image',
                'message': str(e)
            }), 400
        
        # Get top_k parameter
        top_k = request.args.get('top_k', default=5, type=int)
        if top_k <= 0 or top_k > 10:
            top_k = 5
        
        # Reset file pointer after validation
        file.seek(0)
        
        # Classify the image
        try:
            predictions = classifier.classify_image(file, top_k=top_k)
            
            return jsonify({
                'status': 'success',
                'filename': secure_filename(file.filename or 'unknown'),
                'predictions': predictions,
                'total_predictions': len(predictions)
            }), 200
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return jsonify({
                'error': 'Classification failed',
                'message': f'Error during image classification: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in classify_single_image: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/classify/batch', methods=['POST'])
def classify_batch_images():
    """
    Classify multiple images
    
    Expected request: multipart/form-data with multiple 'images' file fields
    Optional query parameter: top_k (default: 5)
    """
    try:
        # Check if images are provided
        if 'images' not in request.files:
            return jsonify({
                'error': 'No images provided',
                'message': 'Please provide image files in the "images" field'
            }), 400
        
        files = request.files.getlist('images')
        
        # Check if files are selected
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                'error': 'No files selected',
                'message': 'Please select files to upload'
            }), 400
        
        # Validate maximum number of files (limit to 10 for performance)
        if len(files) > 10:
            return jsonify({
                'error': 'Too many files',
                'message': 'Maximum 10 files allowed per batch request'
            }), 400
        
        # Validate each file
        valid_files = []
        invalid_files = []
        
        for i, file in enumerate(files):
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                invalid_files.append({
                    'index': i,
                    'filename': file.filename,
                    'error': 'Invalid file format'
                })
                continue
            
            try:
                validate_image_file(file)
                valid_files.append(file)
            except ValueError as e:
                invalid_files.append({
                    'index': i,
                    'filename': file.filename,
                    'error': str(e)
                })
        
        if not valid_files:
            return jsonify({
                'error': 'No valid images',
                'message': 'All provided files are invalid or corrupted',
                'invalid_files': invalid_files
            }), 400
        
        # Get top_k parameter
        top_k = request.args.get('top_k', default=5, type=int)
        if top_k <= 0 or top_k > 10:
            top_k = 5
        
        # Classify the images
        try:
            results = classifier.classify_batch(valid_files, top_k=top_k)
            
            return jsonify({
                'status': 'success',
                'total_images': len(files),
                'valid_images': len(valid_files),
                'invalid_images': len(invalid_files),
                'results': results,
                'invalid_files': invalid_files if invalid_files else None
            }), 200
            
        except Exception as e:
            logger.error(f"Batch classification error: {str(e)}")
            return jsonify({
                'error': 'Batch classification failed',
                'message': f'Error during batch image classification: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in classify_batch_images: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if classifier is loaded
        if classifier.model is None:
            return jsonify({
                'status': 'unhealthy',
                'message': 'ML model not loaded'
            }), 503
        
        return jsonify({
            'status': 'healthy',
            'message': 'API is operational',
            'model': 'MobileNetV2'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'message': f'Health check failed: {str(e)}'
        }), 503

@api_bp.route('/info', methods=['GET'])
def api_info():
    """Get API information and usage instructions"""
    return jsonify({
        'api_name': 'Image Classification API',
        'version': '1.0.0',
        'model': 'MobileNetV2 (ImageNet)',
        'endpoints': {
            '/api/classify': {
                'method': 'POST',
                'description': 'Classify a single image',
                'parameters': {
                    'image': 'Image file (required)',
                    'top_k': 'Number of top predictions (optional, default: 5, max: 10)'
                },
                'supported_formats': ['JPG', 'JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
            },
            '/api/classify/batch': {
                'method': 'POST',
                'description': 'Classify multiple images',
                'parameters': {
                    'images': 'Multiple image files (required, max: 10)',
                    'top_k': 'Number of top predictions per image (optional, default: 5, max: 10)'
                },
                'supported_formats': ['JPG', 'JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
            },
            '/api/health': {
                'method': 'GET',
                'description': 'Check API health status'
            },
            '/api/info': {
                'method': 'GET',
                'description': 'Get API information'
            }
        },
        'limits': {
            'max_file_size': '16MB',
            'max_batch_size': 10,
            'max_predictions': 10
        }
    }), 200
