"""Script para testar o pipeline de treino diretamente."""
import asyncio
import traceback
from app.database import engine, AsyncSessionLocal
from app.models import Base
from ml.pipeline.training import TrainingPipeline


async def main():
    # Criar tabelas se necessário
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        pipeline = TrainingPipeline(session=session, store_id=1)
        try:
            report = await pipeline.run()
            import json
            print(json.dumps(report, indent=2, default=str))
        except Exception as e:
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
