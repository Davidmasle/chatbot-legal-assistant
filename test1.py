from app.services.parser import extract_text
from app.services.chunker import split_text
from app.services.embeddings import save_chunks_with_embeddings
from app.db.models import Document
from app.db.database import async_session

async def process_document(file_path: str, title: str):
    text = extract_text(file_path)
    chunks = split_text(text, chunk_size=500, overlap=100)

    # Сохраняем документ
    async with async_session() as session:
        doc = Document(title=title, file_path=file_path)
        session.add(doc)
        await session.commit()
        await session.refresh(doc)  # чтобы получить document_id

    # Генерируем эмбеддинги локально и сохраняем чанки
    await save_chunks_with_embeddings(doc.id, chunks)
