import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agents.service import answer_customer

load_dotenv()

app = FastAPI(
    title="Northstar AI Support API",
    description="Product-aware customer support served entirely from Render.",
    version="2.0.0",
)

origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=origins != ["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
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
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    intent: str
    products: list[Product] = Field(default_factory=list)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "northstar-ai-support",
        "runtime": "render",
        "ai_provider": "openai" if os.getenv("OPENAI_API_KEY") else "catalog-fallback",
        "firebase_enabled": False,
        "crewai_enabled": False,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return answer_customer(request.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Northstar Support could not process the request.") from exc


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        requested = FRONTEND_DIST / full_path
        if full_path and requested.is_file():
            return FileResponse(requested)
        return FileResponse(FRONTEND_DIST / "index.html")
