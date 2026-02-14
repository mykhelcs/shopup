from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

try:
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
except Exception as e:
    print(f"Error creating database engine: {e}")
    print("TIP: For local development without PostgreSQL, set DATABASE_URL=sqlite+aiosqlite:///./test.db in .env")
    # Fallback to a dummy in-memory sqlite if it absolutely fails to create the engine (though create_async_engine usually lazy connects)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
