import numpy as np
import logging
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import io

logger = logging.getLogger(__name__)

class ImageClassifier:
    def __init__(self):
        """Initialize the image classifier with pre-trained MobileNetV2 model"""
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the pre-trained MobileNetV2 model"""
        try:
            logger.info("Loading MobileNetV2 model...")
            self.model = MobileNetV2(weights='imagenet', include_top=True)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def preprocess_image(self, image_file):
        """
        Preprocess the uploaded image for model prediction

        Args:
            image_file: File object containing the image

        Returns:
            Preprocessed image array ready for prediction
        """
        try:
            # Open and convert image.
            img = Image.open(io.BytesIO(image_file.read()))

            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize to model input size (224x224 for MobileNetV2)
            img = img.resize((224, 224))

            # Convert to array.
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)

            # Preprocess for MobileNetV2.
            img_array = preprocess_input(img_array)

            return img_array

        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ValueError(f"Invalid image format or corrupted file: {str(e)}")

    def classify_image(self, image_file, top_k=5):
        """
        Classify a single image

        Args:
            image_file: File object containing the image
            top_k: Number of top predictions to return

        Returns:
            List of predictions with class names and confidence scores
        """
        try:
            if self.model is None:
                raise RuntimeError("Model not loaded")

            # Preprocess the image
            processed_image = self.preprocess_image(image_file)

            # Make prediction
            predictions = self.model.predict(processed_image)

            # Decode predictions
            decoded_predictions = decode_predictions(predictions, top=top_k)[0]

            # Format results
            results = []
            for pred in decoded_predictions:
                class_id, class_name, confidence = pred
                results.append({
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': float(confidence),
                    'confidence_percentage': f"{confidence * 100:.2f}%"
                })

            logger.info(f"Classification completed. Top prediction: {results[0]['class_name']} ({results[0]['confidence_percentage']})")
            return results

        except Exception as e:
            logger.error(f"Error during classification: {str(e)}")
            raise

    def classify_batch(self, image_files, top_k=5):
        """
        Classify multiple images

        Args:
            image_files: List of file objects containing images
            top_k: Number of top predictions to return for each image

        Returns:
            List of classification results for each image
        """
        results = []
        for i, image_file in enumerate(image_files):
            try:
                # Reset file pointer
                image_file.seek(0)
                classification_result = self.classify_image(image_file, top_k)
                results.append({
                    'image_index': i,
                    'status': 'success',
                    'predictions': classification_result
                })
            except Exception as e:
                logger.error(f"Error classifying image {i}: {str(e)}")
                results.append({
                    'image_index': i,
                    'status': 'error',
                    'error': str(e)
                })

        return results

# Global classifier instance
classifier = ImageClassifier()
