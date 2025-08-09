import os
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Allowed image extensions..
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension

    Args:
        filename: Name of the uploaded file

    Returns:
        Boolean indicating if the file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_file(file):
    """
    Validate that the uploaded file is a valid image

    Args:
        file: File object to validate

    Raises:
        ValueError: If the file is not a valid image
    """
    position = 0
    try:
        # Save current position.
        position = file.tell()

        # Try to open and verify the image
        img = Image.open(io.BytesIO(file.read()))
        img.verify()

        # Check image size (minimum dimensions)
        if img.size[0] < 32 or img.size[1] < 32:
            raise ValueError("Image dimensions too small (minimum 32x32 pixels)")

        # Check image size (maximum dimensions for performance)
        if img.size[0] > 4096 or img.size[1] > 4096:
            raise ValueError("Image dimensions too large (maximum 4096x4096 pixels)")

        # Reset file position
        file.seek(position)

    except Exception as e:
        # Reset file position
        file.seek(position)
        raise ValueError(f"Invalid or corrupted image file: {str(e)}")

def format_file_size(size_bytes):
    """
    Format file size in human readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string with appropriate unit
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"

def get_image_info(file):
    """
    Get basic information about an image file

    Args:
        file: Image file object

    Returns:
        Dictionary with image information
    """
    position = 0
    try:
        position = file.tell()
        img = Image.open(io.BytesIO(file.read()))

        info = {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.size[0],
            'height': img.size[1]
        }

        file.seek(position)
        return info

    except Exception as e:
        file.seek(position)
        logger.error(f"Error getting image info: {str(e)}")
        return None
