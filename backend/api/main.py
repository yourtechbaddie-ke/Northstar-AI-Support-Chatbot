import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.service import answer_customer

load_dotenv()

app = FastAPI(
    title="Northstar AI Support API",
    description="Product-aware customer support powered by CrewAI and Northstar catalog data.",
    version="1.1.0",
)

origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None, max_length=120)


class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    stock: int
    status: str


class ChatResponse(BaseModel):
    message: str
    intent: str
    products: list[Product] = Field(default_factory=list)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "northstar-ai-support",
        "crewai_enabled": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return answer_customer(request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Northstar Support could not process the request.") from exc
