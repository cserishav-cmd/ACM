"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration from environment variables."""

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")

    # Model paths
    SEG_MODEL_PATH: str = os.path.join(MODELS_DIR, "seg_model.keras")
    DISEASE_MODEL_PATH: str = os.path.join(MODELS_DIR, "disease_model.keras")
    VARIETY_MODEL_PATH: str = os.path.join(MODELS_DIR, "variety_model.keras")
    
    # Dataset paths
    CHATBOT_PROMPT_PATH: str = os.path.join(DATA_DIR, "agriculture_chatbot_prompt.pkl")
    COMBINED_DATASETS_PATH: str = os.path.join(DATA_DIR, "wb_datasets_combined.pkl")

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Image processing
    MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", 10485760))  # 10MB
    ALLOWED_EXTENSIONS: list[str] = os.getenv(
        "ALLOWED_EXTENSIONS", "jpg,jpeg,png,webp"
    ).split(",")

    # Model input shapes
    SEG_INPUT_SHAPE: tuple = (224, 224)
    CLASSIFY_INPUT_SHAPE: tuple = (224, 224)


config = Config()
