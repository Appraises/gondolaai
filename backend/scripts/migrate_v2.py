import asyncio
from sqlalchemy import text
from app.database import engine

async def run():
    async with engine.begin() as conn:
        await conn.execute(
            text("""ALTER TABLE products ADD COLUMN base_elasticity NUMERIC(10, 4)""")
        )
        await conn.execute(
            text("""ALTER TABLE products ADD COLUMN cross_elasticity VARCHAR(5000)""")
        )
        await conn.execute(
            text("""ALTER TABLE products ADD COLUMN baseline_demand NUMERIC(10, 2)""")
        )
        print("Tabelas V2 Pricing (Elasticidade) criadas com sucesso.")

if __name__ == "__main__":
    asyncio.run(run())

