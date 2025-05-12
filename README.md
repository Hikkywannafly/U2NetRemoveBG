# Hướng dẫn sử dụng API Tạo Ảnh Thẻ

## Giới thiệu

API Tạo Ảnh Thẻ là một dịch vụ backend sử dụng FastAPI cho phép người dùng tải lên ảnh, xóa phông nền tự động và tạo ảnh thẻ với nhiều kích thước chuẩn khác nhau.

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Pip (trình quản lý gói Python)

### Các bước cài đặt

1. Clone repository về máy:

```bash
git clone https://github.com/yourusername/photo-id-api.git
cd photo-id-api
```

2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

3. Khởi động server:

```bash
python -m app.main
```

Server sẽ chạy tại địa chỉ: http://localhost:8000

## Cấu trúc API

### Lấy danh sách kích thước ảnh thẻ

```
GET /api/photo/sizes
```

**Phản hồi:**

```json
{
  "sizes": [
    {
      "width": 35,
      "height": 45,
      "name": "3x4",
      "description": "Ảnh thẻ 3x4 cm"
    },
    {
      "width": 40,
      "height": 60,
      "name": "4x6",
      "description": "Ảnh thẻ 4x6 cm"
    },
    ...
  ]
}
```

### Tải lên và xử lý ảnh

```
POST /api/photo/upload
```

**Tham số:**

- `file`: File ảnh cần xử lý (bắt buộc)
- `size`: Kích thước ảnh thẻ (tùy chọn, mặc định: "3x4")
- `bg_color`: Màu nền (tùy chọn, mặc định: "255,255,255" - màu trắng)

**Phản hồi:**

```json
{
  "original_url": "/static/uploads/abc123.jpg",
  "removed_bg_url": "/static/results/nobg_abc123.jpg",
  "id_photo_url": "/static/results/idphoto_abc123.jpg",
  "message": "Xử lý ảnh thành công"
}
```

### Xem trước ảnh đã xử lý

```
GET /api/photo/preview/{filename}
```

**Phản hồi:**

```json
{
  "url": "/static/results/idphoto_abc123.jpg"
}
```

## Ví dụ sử dụng

### Sử dụng cURL

```bash
# Lấy danh sách kích thước ảnh thẻ
curl -X GET http://localhost:8000/api/photo/sizes

# Tải lên và xử lý ảnh
curl -X POST http://localhost:8000/api/photo/upload \
  -F "file=@/path/to/your/photo.jpg" \
  -F "size=3x4" \
  -F "bg_color=255,255,255"
```

### Sử dụng JavaScript (Fetch API)

```javascript
// Lấy danh sách kích thước ảnh thẻ
fetch("http://localhost:8000/api/photo/sizes")
  .then((response) => response.json())
  .then((data) => console.log(data));

// Tải lên và xử lý ảnh
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("size", "3x4");
formData.append("bg_color", "255,255,255");

fetch("http://localhost:8000/api/photo/upload", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => {
    console.log(data);
    // Hiển thị ảnh đã xử lý
    document.getElementById("result").src = data.id_photo_url;
  });
```

## Lưu ý

- API sử dụng mô hình briaai/RMBG-1.4 để xóa phông nền, đảm bảo máy chủ có đủ tài nguyên để chạy mô hình này.
- Các file ảnh được lưu trong thư mục `static/uploads` và `static/results`.
- Để đảm bảo hiệu suất tốt nhất, nên sử dụng GPU để xử lý ảnh.

## Xử lý lỗi

API trả về mã lỗi HTTP và thông báo lỗi cụ thể:

- 400: Lỗi đầu vào (file không phải ảnh, tham số không hợp lệ)
- 404: Không tìm thấy tài nguyên
- 500: Lỗi server (lỗi xử lý ảnh, lỗi hệ thống)

## Giấy phép

MIT License
