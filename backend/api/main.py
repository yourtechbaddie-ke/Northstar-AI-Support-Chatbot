import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agents.service import answer_customer

load_dotenv()

app = FastAPI(title="Northstar AI Support", version="1.0.0")
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None

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
    products: list[Product] = []

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "northstar-ai-support"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return answer_customer(request.message)
