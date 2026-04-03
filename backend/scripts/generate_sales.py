"""
Script para gerar vendas sintéticas realistas.

Gera ~90 dias de histórico de vendas para todos os produtos do banco,
simulando padrões reais de supermercado:
- Sazonalidade por dia da semana (sábado vende mais)
- Efeito do pagamento (semana 1 do mês vende mais)
- Volume diferente por categoria/produto
- Ruído aleatório para realismo

Uso: python -m scripts.generate_sales
"""

import asyncio
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

from sqlalchemy import select
from loguru import logger

from app.database import engine, AsyncSessionLocal
from app.models import Base, Product, Sale, SaleItem


# ── Configuração ──
DAYS_OF_HISTORY = 90
SALES_PER_DAY_BASE = 80  # Cupons por dia em média

# Multiplicadores por dia da semana (Seg=0 ... Dom=6)
DAY_OF_WEEK_MULTIPLIER = {
    0: 0.6,   # Segunda - dia mais fraco
    1: 0.7,   # Terça
    2: 0.8,   # Quarta
    3: 0.9,   # Quinta
    4: 1.3,   # Sexta - pré fim de semana
    5: 1.6,   # Sábado - dia mais forte
    6: 1.0,   # Domingo - meia jornada
}

# Multiplicador por semana do mês (efeito salário)
WEEK_OF_MONTH_MULTIPLIER = {
    1: 1.4,   # Pós-pagamento (dia 1-7)
    2: 1.1,   # Ainda com dinheiro
    3: 0.9,   # Apertando
    4: 0.7,   # Pré-pagamento
    5: 0.8,   # Se o mês tiver 5ª semana
}

# Volume base de vendas diárias por categoria
CATEGORY_DAILY_VOLUME = {
    "Bebidas": (3, 15),         # Cada produto vende entre 3-15 un/dia
    "Laticínios": (2, 12),
    "Açougue": (1, 5),          # Carne vende menos unidades, mas valor alto
    "Padaria": (5, 20),         # Pão vende muito
    "FLV": (3, 10),
    "Limpeza": (1, 5),
    "Higiene": (1, 4),
    "Mercearia": (2, 8),
    "Congelados": (1, 4),
    "Pet": (1, 3),
}

# Métodos de pagamento com pesos
PAYMENT_METHODS = [
    ("PIX", 0.40),
    ("Cartão Débito", 0.25),
    ("Cartão Crédito", 0.20),
    ("Dinheiro", 0.15),
]


def _weighted_choice(options: list[tuple[str, float]]) -> str:
    """Escolhe uma opção com probabilidade ponderada."""
    names, weights = zip(*options)
    return random.choices(names, weights=weights, k=1)[0]


def _get_week_of_month(d: date) -> int:
    """Retorna a semana do mês (1-5)."""
    return min((d.day - 1) // 7 + 1, 5)


async def generate_sales():
    """Gera vendas sintéticas para os últimos N dias."""
    logger.info(f"🏭 Gerando {DAYS_OF_HISTORY} dias de vendas sintéticas...")

    # Criar tabelas se não existirem
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Buscar todos os produtos
        result = await session.execute(
            select(Product).where(Product.store_id == 1, Product.is_active == True)
        )
        products = result.scalars().all()

        if not products:
            logger.error("❌ Nenhum produto encontrado! Faça upload do CSV primeiro.")
            return

        logger.info(f"📦 {len(products)} produtos encontrados")

        # Limpar vendas antigas (para poder re-rodar)
        from sqlalchemy import delete
        await session.execute(delete(SaleItem))
        await session.execute(delete(Sale))
        await session.commit()
        logger.info("🗑️ Vendas anteriores removidas")

        total_sales = 0
        total_items = 0
        today = date.today()
        start_date = today - timedelta(days=DAYS_OF_HISTORY)

        # Gerar vendas dia a dia
        for day_offset in range(DAYS_OF_HISTORY):
            current_date = start_date + timedelta(days=day_offset)
            dow = current_date.weekday()
            wom = _get_week_of_month(current_date)

            # Calcular número de cupons do dia
            day_mult = DAY_OF_WEEK_MULTIPLIER.get(dow, 1.0)
            week_mult = WEEK_OF_MONTH_MULTIPLIER.get(wom, 1.0)
            noise = random.uniform(0.8, 1.2)
            num_sales = int(SALES_PER_DAY_BASE * day_mult * week_mult * noise)

            for sale_idx in range(num_sales):
                # Horário aleatório entre 7h e 22h
                hour = random.randint(7, 21)
                minute = random.randint(0, 59)
                sale_time = datetime(
                    current_date.year, current_date.month, current_date.day,
                    hour, minute, random.randint(0, 59)
                )

                # Cada cupom tem entre 2 e 12 itens
                num_items = random.randint(2, 12)
                sale_products = random.sample(products, min(num_items, len(products)))

                sale = Sale(
                    store_id=1,
                    sale_id=f"CUP-{current_date.strftime('%Y%m%d')}-{sale_idx+1:04d}",
                    timestamp=sale_time,
                    total=Decimal("0"),
                    payment_method=_weighted_choice(PAYMENT_METHODS),
                )
                session.add(sale)
                await session.flush()

                sale_total = Decimal("0")

                for product in sale_products:
                    # Volume de venda baseado na categoria
                    cat_range = CATEGORY_DAILY_VOLUME.get(
                        product.category, (1, 5)
                    )
                    # Para um único cupom, quantidade é menor
                    qty = Decimal(str(random.randint(1, min(cat_range[1], 5))))

                    # Desconto aleatório (10% de chance de ter desconto)
                    discount = Decimal("0")
                    if random.random() < 0.10:
                        discount_pct = random.choice([5, 10, 15, 20])
                        discount = (product.unit_price * qty * discount_pct / 100).quantize(
                            Decimal("0.01")
                        )

                    item_total = (product.unit_price * qty) - discount
                    sale_total += item_total

                    sale_item = SaleItem(
                        sale_id_fk=sale.id,
                        product_id=product.id,
                        quantity=qty,
                        unit_price=product.unit_price,
                        discount=discount,
                    )
                    session.add(sale_item)
                    total_items += 1

                sale.total = sale_total.quantize(Decimal("0.01"))
                total_sales += 1

            # Commit a cada dia (para não acumular demais na memória)
            await session.commit()

            if (day_offset + 1) % 10 == 0:
                logger.info(
                    f"  📅 {day_offset + 1}/{DAYS_OF_HISTORY} dias gerados "
                    f"({total_sales} cupons, {total_items} itens)"
                )

        logger.info(
            f"✅ Geração completa!\n"
            f"   📊 {total_sales:,} cupons fiscais\n"
            f"   📦 {total_items:,} itens vendidos\n"
            f"   📅 {DAYS_OF_HISTORY} dias de histórico"
        )


if __name__ == "__main__":
    asyncio.run(generate_sales())
