from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from PIL import Image
import io

from src.config import SUPPORTED_FORMATS, MAX_FILE_SIZE
from src.image_processor import ImageProcessor

router = APIRouter()

@router.post("/remove-bg/")
async def remove_bg(file: UploadFile = File(...)):
    # Validate file size
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large. Maximum size is 10MB")
    
    # Validate file type
    if file.content_type not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload JPEG or PNG images")
    
    try:
        # Process image
        image = Image.open(io.BytesIO(contents))
        # Remove background
        output = ImageProcessor.remove_background(image)
        
        # Convert to bytes
        img_bytes = ImageProcessor.image_to_bytes(output)
        
        # Return binary response with proper headers
        return Response(
            content=img_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "max-age=3600",
                "Content-Disposition": "attachment; filename=removed_bg.png"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")