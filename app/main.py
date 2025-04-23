from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, APP_DESCRIPTION, APP_VERSION, CORS_ORIGINS, STATIC_DIR
from app.routers import photo

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
app.include_router(photo.router)

# Mount thư mục static để phục vụ file tĩnh
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return {"message": "Chào mừng đến với API Tạo Ảnh Thẻ"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)