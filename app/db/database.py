import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/legaldb"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
