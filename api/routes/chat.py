"""Chat API route for conversational AI follow-ups."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from api.schemas.response import PredictionResponse, ErrorResponse
from src.chatbot import ChatbotService

router = APIRouter()

# Shared chatbot instance
chatbot = ChatbotService()

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    pipeline_results: Optional[Dict[str, Any]] = None

@router.post(
    "",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Chatbot follow-up query",
    description="Ask follow-up questions to the agricultural AI using previous inference context.",
)
async def chat_with_bot(request: ChatRequest):
    """Run a conversational turn with the agricultural chatbot."""
    try:
        if not request.messages:
            raise ValueError("Messages list cannot be empty.")
            
        messages_dict = [{"role": "assistant" if msg.role == "ai" else msg.role, "content": msg.text} for msg in request.messages]
        
        reply = await chatbot.chat(
            user_messages=messages_dict,
            pipeline_results=request.pipeline_results
        )

        return PredictionResponse(
            success=True,
            message="Chat completed",
            data={"reply": reply},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
