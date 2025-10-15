from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

Base = declarative_base()

from sqlalchemy import ARRAY

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, nullable=True)  
    file_path = Column(String, nullable=False)

class DocChunk(Base):
    __tablename__ = "doc_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(ARRAY(DOUBLE_PRECISION), nullable=False)  
