import os
from dotenv import load_dotenv
load_dotenv()
os.environ.setdefault("TMPDIR", "/tmp")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent import run_agent

app = FastAPI(title="AI Agent Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama-3.1-8b-instant"}

@app.post("/chat")
async def chat(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    result  = run_agent(request.question, history)
    return result
