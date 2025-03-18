from PIL import Image
from rembg import remove
import io
import cv2
import numpy as np
import os

class ImageProcessor:
    @staticmethod
    def detect_face(image: Image.Image) -> bool:
        """Check if the image contains a human face."""
        try:
            # Convert PIL Image to cv2 format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cascade_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'haarcascade_frontalface_default.xml')
            if not os.path.exists(cascade_path):
                raise FileNotFoundError("Face detection model file not found. Please ensure the model file is present in the models directory.")
            
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if face_cascade.empty():
                raise ValueError("Failed to load face detection model. The model file may be corrupted.")
                
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
            return len(faces) > 0
        except Exception as e:
            raise ValueError(f"Face detection failed: {str(e)}. Please ensure the image is valid and try again.")

    @staticmethod
    def remove_background(image: Image.Image) -> Image.Image:
        """
        Remove the background from a portrait photo.
        
        Args:
            image (PIL.Image.Image): Input portrait photo
            
        Returns:
            PIL.Image.Image: Processed image with background removed
            
        Raises:
            ValueError: If the input is not a portrait photo or invalid
            Exception: If background removal fails
        """
        try:
            if not isinstance(image, Image.Image):
                raise ValueError("Input must be a PIL Image object. Please provide a valid image.")

            # Validate image mode and convert if necessary
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')

            # Check if image contains a face
            try:
                if not ImageProcessor.detect_face(image):
                    raise ValueError("No human face detected in the image. Please provide a clear portrait photo.")
            except ValueError as ve:
                if "Face detection failed" in str(ve):
                    # If face detection fails due to technical issues, proceed with background removal
                    pass
                else:
                    raise ve
                
            # Use rembg with optimized settings for portrait photos
            result = remove(image, post_process_mask=True)
            
            if isinstance(result, Image.Image):
                return result
            elif isinstance(result, bytes):
                try:
                    return Image.open(io.BytesIO(result))
                except Exception as e:
                    raise ValueError(f"Failed to process background removal result: {str(e)}")
            elif isinstance(result, np.ndarray):
                try:
                    return Image.fromarray(result)
                except Exception as e:
                    raise ValueError(f"Failed to convert background removal result: {str(e)}")
                    
            raise ValueError("Unexpected return type from background removal. Please try again.")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise Exception(f"Failed to remove background: {str(e)}. Please ensure the image is valid and try again.")
    
    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
        """
        Convert a PIL Image to bytes.
        
        Args:
            image (PIL.Image.Image): Image to convert
            format (str): Output image format (default: 'PNG')
            
        Returns:
            bytes: Image converted to bytes
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()