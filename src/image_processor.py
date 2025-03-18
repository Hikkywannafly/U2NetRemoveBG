from PIL import Image
from rembg import remove
import io

class ImageProcessor:
    @staticmethod
    def remove_background(image: Image.Image) -> Image.Image:
        """
        Remove the background from an input image.
        
        Args:
            image (PIL.Image.Image): Input image to process
            
        Returns:
            PIL.Image.Image: Processed image with background removed
            
        Raises:
            ValueError: If the input image is invalid
            Exception: If background removal fails
        """
        if not isinstance(image, Image.Image):
            raise ValueError("Input must be a PIL Image object")
            
        try:
            return remove(image)
        except Exception as e:
            raise Exception(f"Failed to remove background: {str(e)}")
    
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