"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Limit TensorFlow memory usage for Render Free Tier (512MB RAM)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" 
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from api.routes.predict import router as predict_router
from api.routes.weather import router as weather_router
from api.routes.chat import router as chat_router
from src.pipeline import PipelineService
from src.chatbot import ChatbotService

load_dotenv()

app = FastAPI(
    title="Rice AI System",
    description="AI-powered rice crop analysis — segmentation, disease detection, and variety classification",
    version="1.0.0",
)

from fastapi import Request
from fastapi.responses import JSONResponse

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"Server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Load models on startup
pipeline_service = PipelineService()


@app.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "Welcome to the Rice AI System API",
        "docs": "/docs",
        "health": "/api/health",
        "status": "online"
    }


@app.on_event("startup")
async def startup_event():
    """Startup events (load models into memory)."""
    # Initialize ChatbotService singleton
    chatbot = ChatbotService()
    
    # Pre-load models to avoid timeouts during first request
    try:
        pipeline_service.load_models()
        print("[OK] All models loaded into memory.")
    except Exception as e:
        print(f"[Error] Failed to load models on startup: {e}")
        
    print("[OK] Backend services initialized.")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": pipeline_service.models_loaded,
    }


# Register routes
app.include_router(predict_router, prefix="/api/predict", tags=["prediction"])
app.include_router(weather_router, prefix="/api/weather", tags=["weather"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
