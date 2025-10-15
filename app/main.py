from fastapi import FastAPI, UploadFile, File, Form, Body, Request, WebSocket
from pathlib import Path
import shutil

from app.db.database import async_session, engine
from app.db.models import Base, Document, DocChunk
from app.services.parser import extract_text
from app.services.chunker import split_text
from app.services.embeddings import save_chunks_with_embeddings
import numpy as np
import aiohttp
import asyncio
import json

from app.services.embeddings import get_query_embedding
from app.services.retriever import retrieve_relevant_chunks
from app.services.llm import generate_answer
from app.services.ollama_client import OllamaClient
from app.services.embeddings import embed_text_local

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")


ollama = OllamaClient(host="http://127.0.0.1:11434", model="llama3")

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3 

class QueryResponse(BaseModel):
    question: str
    answer: str
    source_chunks: List[int]
    source_texts: List[str]

app = FastAPI(title="Legal Assistant MVP")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized!")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), title: str = Form(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(str(file_path))
    chunks = split_text(text, chunk_size=500, overlap=100)

    async with async_session() as session:
        doc = Document(title=title, file_path=str(file_path))
        session.add(doc)
        await session.commit()
        await session.refresh(doc) 

    await save_chunks_with_embeddings(doc.id, chunks)

    return {
        "status": "ok",
        "message": f"Документ '{title}' успешно загружен",
        "document_id": doc.id,
        "chunks_count": len(chunks)
    }


@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    question = request.question
    top_k = request.top_k or 3

    q_emb = np.array(await embed_text_local(question))

    async with async_session() as session:
        result = await session.execute(
            DocChunk.__table__.select()
        )
        chunks = result.fetchall()

    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    scored_chunks = []
    for chunk in chunks:
        emb = np.array(chunk.embedding)
        score = cosine_sim(q_emb, emb)
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored_chunks[:top_k]

    context_texts = [c.content for _, c in top_chunks]
    context_ids = [c.id for _, c in top_chunks]
    prompt = f"""Ты юридический ассистент. Используй следующие фрагменты документов для ответа на вопрос:
Вопрос: {question}
Контекст:
{chr(10).join(context_texts)}
Отвечай всегда на русском языке, максимально подробно, используя только данные из контекста.
Если информации нет - честно скажи, что данных нет."""
    
    answer = ollama.generate(prompt)

    return QueryResponse(
        question=question,
        answer=answer,
        source_chunks=context_ids,
        source_texts=context_texts
    )

@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        question = data.get("question")
        if not question:
            await websocket.send_json({"error": "No question provided"})
            return

        url = f"{ollama.host}/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {"model": ollama.model, "prompt": question}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                async for raw_line in resp.content:
                    line = raw_line.decode('utf-8').strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        text_part = chunk.get("response", "")
                        if text_part:
                            await websocket.send_json({"text": text_part})
                        if chunk.get("done", False):
                            await websocket.send_json({"done": True})
                            break
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
