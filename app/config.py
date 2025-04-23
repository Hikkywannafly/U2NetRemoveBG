import os
from pathlib import Path

# Thư mục gốc của ứng dụng
BASE_DIR = Path(__file__).resolve().parent.parent

# Thư mục lưu trữ file tĩnh
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
RESULTS_DIR = os.path.join(STATIC_DIR, "results")

# Đảm bảo các thư mục tồn tại
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# DPI tiêu chuẩn cho ảnh in
DPI = 300

# Cấu hình CORS
CORS_ORIGINS = ["*"]  # Trong môi trường production, hãy giới hạn nguồn gốc

# Thông tin ứng dụng
APP_NAME = "Ứng dụng Tạo Ảnh Thẻ API"
APP_DESCRIPTION = "API cho ứng dụng tạo ảnh thẻ với chức năng xóa phông nền"
APP_VERSION = "1.0.0"