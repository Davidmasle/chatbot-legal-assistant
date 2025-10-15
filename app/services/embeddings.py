from typing import List
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import DocChunk
from app.db.database import async_session

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

async def embed_text_local(text: str) -> List[float]:
    vector = model.encode(text, normalize_embeddings=True)  
    return vector.tolist()


async def save_chunks_with_embeddings(document_id: int, chunks: list):
    async with async_session() as session:
        for idx, chunk in enumerate(chunks):
            embedding_vector = await embed_text_local(chunk)
            doc_chunk = DocChunk(
                document_id=document_id,
                chunk_index=idx,
                content=chunk,
                embedding=embedding_vector
            )
            session.add(doc_chunk)
        await session.commit()
    print(f"{len(chunks)} chunks saved with embeddings for document_id={document_id}")

def get_query_embedding(text: str) -> List[float]:
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()