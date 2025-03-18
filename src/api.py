from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from PIL import Image
import io

from src.config import SUPPORTED_FORMATS, MAX_FILE_SIZE
from src.image_processor import ImageProcessor

router = APIRouter()

@router.post("/remove-bg/")
async def remove_bg(file: UploadFile = File(...)):
    try:
        # Validate file size
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File size too large. Maximum size is {MAX_FILE_SIZE/(1024*1024)}MB")
        
        # Validate file type
        if file.content_type not in SUPPORTED_FORMATS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Please upload one of: {', '.join(SUPPORTED_FORMATS)}")
        
        try:
            # Process image
            try:
                image = Image.open(io.BytesIO(contents))
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid image file. Please ensure the file is a valid image.")
            
            # Validate image format
            if not image.format or image.format.upper() not in ['JPEG', 'PNG']:
                raise HTTPException(status_code=400, detail="Invalid image format. Please upload JPEG or PNG images")
            
            try:
                # Remove background
                output = ImageProcessor.remove_background(image)
                
                # Convert to bytes
                img_bytes = ImageProcessor.image_to_bytes(output)
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

            
            # Return binary response with proper headers
            return Response(
                content=img_bytes,
                media_type="image/png",
                headers={
                    "Cache-Control": "max-age=3600",
                    "Content-Disposition": "attachment; filename=removed_bg.png"
                }
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")