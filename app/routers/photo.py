from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
import shutil
from pathlib import Path

from app.models import PhotoResponse, PhotoSize, PhotoSizeResponse
from app.utils import generate_unique_filename, PHOTO_SIZES
from app.image_processing import remove_background, create_id_photo
from app.image_utils import add_border_to_photo, create_photo_sheet

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
    bg_color: Optional[str] = Form("255,255,255"),
    border_enabled: Optional[bool] = Form(False),
    border_width: Optional[int] = Form(2),
    border_color: Optional[str] = Form("0,0,0"),
    sheet_enabled: Optional[bool] = Form(False),
    sheet_rows: Optional[int] = Form(4),
    sheet_cols: Optional[int] = Form(6),
    sheet_spacing: Optional[int] = Form(10)
):
    """
    Upload ảnh và xử lý:
    1. Lưu ảnh gốc
    2. Xóa phông nền
    3. Tạo ảnh thẻ với kích thước chuẩn
    4. Thêm viền (nếu được yêu cầu)
    5. Tạo sheet ảnh thẻ (nếu được yêu cầu)
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
        id_photo_with_border_path = os.path.join("static", "results", f"border_{filename}")
        photo_sheet_path = os.path.join("static", "results", f"sheet_{filename}")
        
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
        id_photo_with_border_url = None
        photo_sheet_url = None
        
        # Thêm viền nếu được yêu cầu
        if border_enabled:
            try:
                border_color_tuple = tuple(map(int, border_color.split(',')))
                if len(border_color_tuple) != 3:
                    border_color_tuple = (0, 0, 0)
            except:
                border_color_tuple = (0, 0, 0)
            
            add_border_to_photo(id_photo_path, id_photo_with_border_path, border_width, border_color_tuple)
            id_photo_with_border_url = f"{base_url}/results/border_{filename}"
            
            # Sử dụng ảnh có viền cho sheet nếu cả hai được yêu cầu
            sheet_input_path = id_photo_with_border_path
        else:
            sheet_input_path = id_photo_path
        
        # Tạo sheet ảnh thẻ nếu được yêu cầu
        if sheet_enabled:
            create_photo_sheet(sheet_input_path, photo_sheet_path, sheet_rows, sheet_cols, sheet_spacing, bg_color_tuple)
            photo_sheet_url = f"{base_url}/results/sheet_{filename}"
        
        return {
            "original_url": original_url,
            "removed_bg_url": removed_bg_url,
            "id_photo_url": id_photo_url,
            "id_photo_with_border_url": id_photo_with_border_url,
            "photo_sheet_url": photo_sheet_url,
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

@router.post("/add-border", response_model=PhotoResponse)
async def add_border(
    file_path: str = Form(...),
    border_width: Optional[int] = Form(2),
    border_color: Optional[str] = Form("0,0,0")
):
    """
    Thêm viền cho ảnh thẻ:
    1. Lấy ảnh từ đường dẫn
    2. Thêm viền với độ rộng và màu chỉ định
    3. Trả về URL ảnh có viền
    """
    try:
        # Kiểm tra đường dẫn file
        if not file_path.startswith("/static/"):
            raise HTTPException(status_code=400, detail="Đường dẫn file không hợp lệ")
            
        # Chuyển đổi đường dẫn tương đối thành đường dẫn tuyệt đối
        relative_path = file_path.replace("/static/", "")
        input_path = os.path.join("static", relative_path)
        
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        # Tạo tên file đầu ra
        filename = os.path.basename(input_path)
        output_filename = f"border_{filename}"
        output_path = os.path.join("static", "results", output_filename)
        
        # Chuyển đổi border_color từ chuỗi sang tuple
        try:
            border_color_tuple = tuple(map(int, border_color.split(',')))
            if len(border_color_tuple) != 3:
                border_color_tuple = (0, 0, 0)
        except:
            border_color_tuple = (0, 0, 0)
        
        # Thêm viền cho ảnh
        add_border_to_photo(input_path, output_path, border_width, border_color_tuple)
        
        # Xác định các URL
        base_url = "/static"
        original_url = file_path
        id_photo_with_border_url = f"{base_url}/results/{output_filename}"
        
        # Trả về kết quả
        return {
            "original_url": original_url,
            "removed_bg_url": original_url,  # Giả sử file_path là ảnh đã xóa nền
            "id_photo_url": original_url,     # Giả sử file_path là ảnh thẻ
            "id_photo_with_border_url": id_photo_with_border_url,
            "message": "Thêm viền cho ảnh thành công"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm viền: {str(e)}")

@router.post("/create-sheet", response_model=PhotoResponse)
async def create_sheet(
    file_path: str = Form(...),
    rows: Optional[int] = Form(4),
    cols: Optional[int] = Form(6),
    spacing: Optional[int] = Form(10),
    bg_color: Optional[str] = Form("255,255,255")
):
    """
    Tạo sheet ảnh thẻ:
    1. Lấy ảnh từ đường dẫn
    2. Tạo sheet với số hàng, số cột và khoảng cách chỉ định
    3. Trả về URL sheet ảnh thẻ
    """
    try:
        # Kiểm tra đường dẫn file
        if not file_path.startswith("/static/"):
            raise HTTPException(status_code=400, detail="Đường dẫn file không hợp lệ")
            
        # Chuyển đổi đường dẫn tương đối thành đường dẫn tuyệt đối
        relative_path = file_path.replace("/static/", "")
        input_path = os.path.join("static", relative_path)
        
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        # Tạo tên file đầu ra
        filename = os.path.basename(input_path)
        output_filename = f"sheet_{filename}"
        output_path = os.path.join("static", "results", output_filename)
        
        # Chuyển đổi bg_color từ chuỗi sang tuple
        try:
            bg_color_tuple = tuple(map(int, bg_color.split(',')))
            if len(bg_color_tuple) != 3:
                bg_color_tuple = (255, 255, 255)
        except:
            bg_color_tuple = (255, 255, 255)
        
        # Tạo sheet ảnh thẻ
        create_photo_sheet(input_path, output_path, rows, cols, spacing, bg_color_tuple)
        
        # Xác định các URL
        base_url = "/static"
        original_url = file_path
        photo_sheet_url = f"{base_url}/results/{output_filename}"
        
        # Trả về kết quả
        return {
            "original_url": original_url,
            "removed_bg_url": original_url,  # Giả sử file_path là ảnh đã xóa nền
            "id_photo_url": original_url,     # Giả sử file_path là ảnh thẻ
            "photo_sheet_url": photo_sheet_url,
            "message": "Tạo sheet ảnh thẻ thành công"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo sheet ảnh thẻ: {str(e)}")