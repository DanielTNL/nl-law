from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from app.settings import BACKEND_CORS_ORIGINS, PORT
from app.retriever import semantic_search
from app.generator import answer

app = FastAPI(title="NL Law Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskIn(BaseModel):
    question: str
    top_k: int = 5

@app.post("/ask")
async def ask(body: AskIn):
    hits = await semantic_search(body.question, top_k=body.top_k)
    if not hits:
        return {"answer":"Geen relevante bepalingen gevonden.","sources":[]}
    ans = await answer(body.question, hits)
    return {"answer": ans, "sources": hits}
