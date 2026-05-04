"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

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

frontend_origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Startup events (models will be lazy-loaded on first request)."""
    # Initialize ChatbotService singleton
    chatbot = ChatbotService()
    print("[OK] Backend services initialized. Models will be lazy-loaded.")


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
