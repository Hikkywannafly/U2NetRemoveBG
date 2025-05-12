from pydantic import BaseModel
from typing import Optional, List

class PhotoResponse(BaseModel):
    original_url: str
    removed_bg_url: str
    id_photo_url: Optional[str] = None
    id_photo_with_border_url: Optional[str] = None  # URL ảnh thẻ có viền
    photo_sheet_url: Optional[str] = None  # URL sheet ảnh thẻ
    message: str

class PhotoSize(BaseModel):
    width: int
    height: int
    name: str
    description: Optional[str] = None

class PhotoSizeResponse(BaseModel):
    sizes: List[PhotoSize]