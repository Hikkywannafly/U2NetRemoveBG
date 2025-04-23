from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
import shutil
from pathlib import Path

from app.models import PhotoResponse, PhotoSize, PhotoSizeResponse
from app.utils import generate_unique_filename, PHOTO_SIZES
from app.image_processing import remove_background, create_id_photo

router = APIRouter(
    prefix="/api/photo",
    tags=["photo"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sizes", response_model=PhotoSizeResponse)
async def get_photo_sizes():
    """Lấy danh sách các kích thước ảnh thẻ hỗ trợ"""
    sizes = [PhotoSize(**size) for size in PHOTO_SIZES]
    return {"sizes": sizes}

@router.post("/upload", response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    size: Optional[str] = Form("3x4"),
    bg_color: Optional[str] = Form("255,255,255")
):
    """
    Upload ảnh và xử lý:
    1. Lưu ảnh gốc
    2. Xóa phông nền
    3. Tạo ảnh thẻ với kích thước chuẩn
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File phải là ảnh")
    
    try:
        # Tạo tên file duy nhất
        filename = generate_unique_filename(file.filename)
        
        # Đường dẫn lưu file
        original_path = os.path.join("static", "uploads", filename)
        removed_bg_path = os.path.join("static", "results", f"nobg_{filename}")
        id_photo_path = os.path.join("static", "results", f"idphoto_{filename}")
        
        # Lưu file gốc
        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Xóa phông nền
        remove_background(original_path, removed_bg_path)
        
        # Chuyển đổi bg_color từ chuỗi sang tuple
        try:
            bg_color_tuple = tuple(map(int, bg_color.split(',')))
            if len(bg_color_tuple) != 3:
                bg_color_tuple = (255, 255, 255)
        except:
            bg_color_tuple = (255, 255, 255)
        
        # Tạo ảnh thẻ
        create_id_photo(removed_bg_path, id_photo_path, size, bg_color_tuple)
        
        # Tạo URL cho các ảnh
        base_url = "/static"
        original_url = f"{base_url}/uploads/{filename}"
        removed_bg_url = f"{base_url}/results/nobg_{filename}"
        id_photo_url = f"{base_url}/results/idphoto_{filename}"
        
        return {
            "original_url": original_url,
            "removed_bg_url": removed_bg_url,
            "id_photo_url": id_photo_url,
            "message": "Xử lý ảnh thành công"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý ảnh: {str(e)}")

@router.get("/preview/{filename}")
async def preview_photo(filename: str):
    """Xem trước ảnh đã xử lý"""
    file_path = os.path.join("static", "results", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")
    
    return {"url": f"/static/results/{filename}"}