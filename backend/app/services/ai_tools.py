"""
Ferramentas (Tools) mapeadas para o Gemini.
Essas funções batem no banco de dados e retornam uma string limpa para o LLM interpretar.
"""

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from typing import Optional

from app.models.product import Product
from app.models.sale import SaleItem, Sale
from app.models.alert import Alert
from app.models.prediction import Prediction


async def tool_search_stock(session: AsyncSession, product_name: str, store_id: int) -> str:
    """Busca o estoque atual de um produto."""
    query = (
        select(Product)
        .where(Product.store_id == store_id)
        .where(Product.name.ilike(f"%{product_name}%"))
        .limit(5)
    )
    result = await session.execute(query)
    products = result.scalars().all()
    
    if not products:
        return f"Nenhum produto encontrado com o nome '{product_name}'."
    
    output = []
    for p in products:
        output.append(f"- {p.name} | Estoque: {p.stock_qty} | Preço Atual: R$ {p.unit_price:.2f}")
    
    return "\n".join(output)


async def tool_get_active_alerts(session: AsyncSession, store_id: int) -> str:
    """Busca os 10 alertas ativos mais críticos (ruptura ou encalhe)."""
    query = (
        select(Alert, Product.name)
        .join(Product, Product.id == Alert.product_id)
        .where(Alert.store_id == store_id, Alert.is_read == False)
        .order_by(Alert.severity.asc(), Alert.created_at.desc())  # critical, info, warning (Mapeando severity depois na resposta)
        .limit(10)
    )
    result = await session.execute(query)
    rows = result.all()
    
    if not rows:
        return "Nenhum alerta crítico novo na loja hoje. Tudo sob controle!"
    
    output = []
    for alert, prod_name in rows:
        output.append(
            f"[{alert.severity.upper()}] TIPO: {alert.alert_type} | PRODUTO: {prod_name} | "
            f"MENSAGEM: {alert.message} | AÇÃO SUGERIDA: {alert.suggested_action}"
        )
        
    return "\n".join(output)


async def tool_get_sales_today(session: AsyncSession, store_id: int, category: str = "") -> str:
    """Retorna o faturamento das vendas (hoje ou últimos 7 dias caso hoje seja 0)."""
    # Para demonstração no mock (como criamos dados de -90 dias até hoje), pegamos do banco a venda mais recente real.
    # Primeiro achamos o último dia que teve venda
    query_last_sale = select(func.max(Sale.timestamp)).where(Sale.store_id == store_id)
    result_last = await session.execute(query_last_sale)
    last_date = result_last.scalar()
    
    if not last_date:
        return "Nenhuma venda registrada até o momento na loja."
        
    start_date = last_date.replace(hour=0, minute=0, second=0)
    
    query = (
        select(func.sum(SaleItem.quantity * SaleItem.unit_price).label("faturamento"), func.sum(SaleItem.quantity).label("volume"))
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .join(Product, Product.ean == SaleItem.product_ean)
        .where(Sale.store_id == store_id, Sale.timestamp >= start_date)
    )
    
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    
    result = await session.execute(query)
    row = result.first()
    
    faturamento = row.faturamento or 0
    volume = row.volume or 0
    
    data_str = last_date.strftime("%d/%m/%Y")
    
    cat_text = f" da categoria '{category}'" if category else ""
    return f"No relatório mais recente (referência: {data_str}), as vendas{cat_text} foram de R$ {faturamento:.2f} com {volume:g} unidades vendidas."
