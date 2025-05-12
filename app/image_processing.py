import os
import torch
from PIL import Image
import numpy as np
import cv2
from transformers import pipeline

# Tạo biến toàn cục cho mô hình để tránh tải lại mỗi lần gọi hàm
bria_model = None

def remove_background(input_path, output_path):
    """
    Xóa phông nền của ảnh sử dụng mô hình briaai/RMBG-1.4 và lưu kết quả
    """
    # Đảm bảo thư mục đầu ra tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Sử dụng mô hình briaai/RMBG-1.4 để xóa phông nền
        print(f"Đang xử lý xóa phông nền với briaai/RMBG-1.4, đường dẫn ảnh: {input_path}")
        
        # Kiểm tra file tồn tại
        if not os.path.exists(input_path):
            raise Exception(f"File không tồn tại: {input_path}")
        
        # Tải mô hình sử dụng pipeline (giống như trong server.py)
        global bria_model
        if bria_model is None:
            bria_model = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True, device="cpu")
        
        # Đọc ảnh đầu vào
        input_img = Image.open(input_path).convert("RGB")
        
        # Xử lý ảnh với mô hình
        print("Đang xóa nền ảnh...")
        result = bria_model(input_img, return_mask=True)
        
        # Xử lý mask
        mask = result
        if not isinstance(mask, Image.Image):
            mask = Image.fromarray((mask * 255).astype('uint8'))
        
        # Tạo ảnh RGBA với alpha channel từ mask
        no_bg_image = Image.new("RGBA", input_img.size, (0, 0, 0, 0))
        no_bg_image.paste(input_img, mask=mask)
        
        # Lưu ảnh kết quả
        no_bg_image.save(output_path, format='PNG', compress_level=1)
        print(f"Đã xử lý xong ảnh và lưu vào: {output_path}")
        
        # Giải phóng bộ nhớ GPU
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"Lỗi khi sử dụng briaai/RMBG-1.4: {str(e)}")
        raise Exception(f"Không thể xóa nền ảnh: {str(e)}")
    
    return output_path

def create_id_photo(input_path, output_path, size_name="3x4", bg_color=(255, 255, 255), width_px=None, height_px=None):
    """Tạo ảnh thẻ với kích thước chuẩn và nền trắng, cắt ảnh theo tỉ lệ phù hợp"""
    from app.utils import PHOTO_SIZES, mm_to_pixels
    
    try:
        if width_px is None or height_px is None:
            # Tìm kích thước ảnh thẻ theo tên
            size_info = next((s for s in PHOTO_SIZES if s["name"] == size_name), PHOTO_SIZES[0])
            
            # Chuyển đổi kích thước từ mm sang pixel
            width_px = mm_to_pixels(size_info["width"])
            height_px = mm_to_pixels(size_info["height"])
        
        # Mở ảnh đã xóa phông
        try:
            img = Image.open(input_path)
            
            # Đảm bảo ảnh có kênh alpha
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
                
            # Kiểm tra kênh alpha có hợp lệ không
            if 'A' not in img.getbands():
                raise Exception("Ảnh không có kênh alpha hợp lệ")
                
        except Exception as img_error:
            raise Exception(f"Lỗi khi mở ảnh đã xóa phông: {str(img_error)}")
        
        img_np = np.array(img.convert('RGB'))  # Convert to RGB for OpenCV
        
        # Tạo ảnh nền mới với màu nền đườỉ định
        background = Image.new('RGBA', (width_px, height_px), bg_color + (255,))
        
        try:
            # Chuyển đổi ảnh sang định dạng BGR cho OpenCV
            img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # Tải bộ phát hiện khuôn mặt Haar Cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Phát hiện khuôn mặt
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Lấy khuôn mặt lớn nhất (nếu có nhiều khuôn mặt)
                face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = face
                
                # Tính toán kích thước khuôn mặt
                face_height = h
                face_width = w
                
                # Tính toán tỉ lệ khuôn mặt so với ảnh thẻ
                # Theo tiêu chuẩn, khuôn mặt chiếm khoảng 50-60% chiều cao của ảnh thẻ
                # để chừa không gian cho vai và phần trên đầu
                face_ratio = 0.45  # Giảm xuống 45% để chừa không gian cho vai
                
                # Tính toán kích thước mới của ảnh
                new_face_height = int(height_px * face_ratio)
                scale_factor = new_face_height / face_height
                
                # Tính toán kích thước mới của toàn bộ ảnh
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                
                # Resize ảnh theo tỉ lệ mới
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Tính toán vị trí mới của khuôn mặt sau khi resize
                new_face_left = int(x * scale_factor)
                new_face_top = int(y * scale_factor)
                
                # Tính toán vị trí để đặt khuôn mặt vào phần trên của ảnh thẻ
                # Khuôn mặt nên cách mép trên khoảng 25% chiều cao ảnh thẻ
                top_margin = int(height_px * 0.25)  # Đặt khuôn mặt ở vị trí 25% từ trên xuống
                
                # Tính toán vị trí cắt ảnh
                crop_left = max(0, new_face_left - (width_px - int(face_width * scale_factor)) // 2)
                crop_top = max(0, new_face_top - top_margin)
                
                # Đảm bảo vị trí cắt không vượt quá kích thước ảnh
                if crop_left + width_px > new_width:
                    crop_left = max(0, new_width - width_px)
                if crop_top + height_px > new_height:
                    crop_top = max(0, new_height - height_px)
                
                # Cắt ảnh theo kích thước ảnh thẻ
                if crop_left + width_px <= new_width and crop_top + height_px <= new_height:
                    img_cropped = img_resized.crop((crop_left, crop_top, crop_left + width_px, crop_top + height_px))
                    
                    # Ghép ảnh đã cắt vào nền
                    background.paste(img_cropped, (0, 0), img_cropped)
                else:
                    # Nếu không thể cắt đúng kích thước, resize ảnh để vừa với kích thước ảnh thẻ
                    img_resized = img.resize((width_px, height_px), Image.LANCZOS)
                    background.paste(img_resized, (0, 0), img_resized)
            else:
                # Nếu không tìm thấy khuôn mặt, resize ảnh để vừa với kích thước ảnh thẻ
                # Giữ tỉ lệ và căn giữa
                img_ratio = img.width / img.height
                id_ratio = width_px / height_px
                
                if img_ratio > id_ratio:
                    # Ảnh rộng hơn so với tỉ lệ ảnh thẻ
                    new_height = height_px
                    new_width = int(new_height * img_ratio)
                    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                    left = (new_width - width_px) // 2
                    img_cropped = img_resized.crop((left, 0, left + width_px, height_px))
                else:
                    # Ảnh cao hơn so với tỉ lệ ảnh thẻ
                    new_width = width_px
                    new_height = int(new_width / img_ratio)
                    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                    top = (new_height - height_px) // 4  # Lấy phần trên nhiều hơn
                    img_cropped = img_resized.crop((0, top, width_px, top + height_px))
                
                background.paste(img_cropped, (0, 0), img_cropped)
                
        except Exception as face_error:
            print(f"Lỗi khi xử lý khuôn mặt: {str(face_error)}")
            # Nếu không thể xử lý khuôn mặt, resize ảnh để vừa với kích thước ảnh thẻ
            # Giữ tỉ lệ và căn giữa
            img_ratio = img.width / img.height
            id_ratio = width_px / height_px
            
            if img_ratio > id_ratio:
                # Ảnh rộng hơn so với tỉ lệ ảnh thẻ
                new_height = height_px
                new_width = int(new_height * img_ratio)
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                left = (new_width - width_px) // 2
                img_cropped = img_resized.crop((left, 0, left + width_px, height_px))
            else:
                # Ảnh cao hơn so với tỉ lệ ảnh thẻ
                new_width = width_px
                new_height = int(new_width / img_ratio)
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)
                top = (new_height - height_px) // 4  # Lấy phần trên nhiều hơn
                img_cropped = img_resized.crop((0, top, width_px, top + height_px))
            
            background.paste(img_cropped, (0, 0), img_cropped)
        
        # Lưu ảnh kết quả
        background.save(output_path, format='PNG')
        print(f"Đã tạo ảnh thẻ {size_name} thành công!")
        
    except Exception as e:
        print(f"Lỗi khi tạo ảnh thẻ: {str(e)}")
        # Nếu có lỗi, tạo một ảnh trống với kích thước yêu cầu
        try:
            from app.utils import PHOTO_SIZES, mm_to_pixels
            
            if width_px is None or height_px is None:
                # Tìm kích thước ảnh thẻ theo tên
                size_info = next((s for s in PHOTO_SIZES if s["name"] == size_name), PHOTO_SIZES[0])
                
                # Chuyển đổi kích thước từ mm sang pixel
                width_px = mm_to_pixels(size_info["width"])
                height_px = mm_to_pixels(size_info["height"])
            
            # Tạo ảnh trống
            blank_image = Image.new('RGB', (width_px, height_px), bg_color)
            blank_image.save(output_path, format='PNG')
            print("Đã tạo ảnh trống do xảy ra lỗi!")
        except Exception as blank_error:
            print(f"Lỗi khi tạo ảnh trống: {str(blank_error)}")
    
    return output_path