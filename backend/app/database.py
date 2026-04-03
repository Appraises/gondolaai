from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Loga SQL no console em modo debug
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    Dependency injection do FastAPI.
    Cria uma sessão de banco por request e fecha ao final.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
