from PIL import Image
import os
import shutil

def add_border_to_photo(input_path, output_path, border_width=2, border_color=(0, 0, 0)):
    """Thêm viền cho ảnh thẻ"""
    try:
        img = Image.open(input_path)
        
        # Tạo ảnh mới với kích thước lớn hơn để chứa viền
        width, height = img.size
        new_width = width + 2 * border_width
        new_height = height + 2 * border_width
        
        # Tạo ảnh với viền
        bordered_img = Image.new('RGBA', (new_width, new_height), border_color + (255,))
        bordered_img.paste(img, (border_width, border_width), img if img.mode == 'RGBA' else None)
        
        # Lưu ảnh
        bordered_img.save(output_path, format='PNG')
        print("Đã thêm viền cho ảnh thành công!")
        
    except Exception as e:
        print(f"Lỗi khi thêm viền cho ảnh: {str(e)}")
        # Nếu có lỗi, sao chép ảnh gốc
        try:
            shutil.copy(input_path, output_path)
            print("Đã sao chép ảnh gốc do xảy ra lỗi khi thêm viền!")
        except Exception as copy_error:
            print(f"Lỗi khi sao chép ảnh gốc: {str(copy_error)}")
    
    return output_path

def create_photo_sheet(input_path, output_path, rows=4, cols=6, spacing=10, bg_color=(255, 255, 255)):
    """Tạo bảng ảnh thẻ nhiều ảnh trên một tờ"""
    try:
        img = Image.open(input_path)
        
        # Kích thước ảnh gốc
        width, height = img.size
        
        # Tính toán kích thước tờ ảnh
        sheet_width = cols * width + (cols + 1) * spacing
        sheet_height = rows * height + (rows + 1) * spacing
        
        # Tạo tờ ảnh mới
        sheet = Image.new('RGB', (sheet_width, sheet_height), bg_color)
        
        # Dán ảnh vào tờ
        for row in range(rows):
            for col in range(cols):
                x = spacing + col * (width + spacing)
                y = spacing + row * (height + spacing)
                sheet.paste(img, (x, y), img if img.mode == 'RGBA' else None)
        
        # Lưu tờ ảnh
        sheet.save(output_path, format='PNG')
        print(f"Đã tạo tờ ảnh {rows}x{cols} thành công!")
        
    except Exception as e:
        print(f"Lỗi khi tạo tờ ảnh: {str(e)}")
    
    return output_path