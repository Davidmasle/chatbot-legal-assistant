import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import DocChunk

async def retrieve_relevant_chunks(session: AsyncSession, query_embedding: list[float], top_k: int = 3):
    result = await session.execute(select(DocChunk))
    chunks = result.scalars().all()

    if not chunks:
        return []

    def cosine_sim(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    scored_chunks = [
        (chunk, cosine_sim(query_embedding, chunk.embedding))
        for chunk in chunks
    ]
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    return [c[0] for c in scored_chunks[:top_k]]
