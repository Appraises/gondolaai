"""
Gôndola.ai — Backend API

Motor de IA para supermercados.
Predição de demanda, pricing inteligente e gestão de validade.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.database import engine
from app.models import Base, Store
from app.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown do app."""
    # ── STARTUP ──
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")

    # Criar tabelas no banco (em dev, com SQLite)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("📦 Tabelas do banco criadas/verificadas")

    # Criar loja padrão se não existir
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Store).where(Store.id == 1))
        if not result.scalar_one_or_none():
            default_store = Store(
                name="Supermercado Demo",
                city="Rio de Janeiro",
                state="RJ",
                latitude=-22.9068,
                longitude=-43.1729,
            )
            session.add(default_store)
            await session.commit()
            logger.info("🏪 Loja padrão criada (ID=1): Supermercado Demo")

    yield

    # ── SHUTDOWN ──
    await engine.dispose()
    logger.info("🛑 Servidor encerrado")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API do Gôndola.ai — Motor de inteligência artificial para supermercados.\n\n"
        "Funcionalidades:\n"
        "- 📦 Upload de dados via CSV/XLSX (plug-and-play com qualquer ERP)\n"
        "- 🔍 Consulta de produtos, estoque e vendas\n"
        "- 🤖 Predição de demanda (Sprint 3)\n"
        "- 💬 Chatbot WhatsApp (Sprint 5)\n"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS — permite o frontend React (porta 3000) acessar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # Vite dev server
        "http://localhost:5173",       # Vite alt port
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """Health check — verifica se a API está rodando."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "🟢 online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check detalhado."""
    from app.database import AsyncSessionLocal
    from sqlalchemy import text

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "🟢 connected"
    except Exception as e:
        db_status = f"🔴 error: {str(e)}"

    return {
        "api": "🟢 online",
        "database": db_status,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
    }
