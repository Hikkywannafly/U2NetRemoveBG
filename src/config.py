from typing import Set

# Supported image formats
SUPPORTED_FORMATS: Set[str] = {"image/jpeg", "image/png"}

# Maximum file size (10MB)
MAX_FILE_SIZE: int = 10 * 1024 * 1024

# API Settings
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000

# CORS Settings
CORS_ORIGINS: list = ["*"]  # Adjust this in production
CORS_CREDENTIALS: bool = True
CORS_METHODS: list = ["*"]
CORS_HEADERS: list = ["*"]