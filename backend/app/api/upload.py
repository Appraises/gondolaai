"""
Endpoint de Upload de CSV/XLSX — O coração do MVP.

Permite que o supermercado importe dados de qualquer ERP
simplesmente fazendo upload de uma planilha.
"""

from fastapi import APIRouter, UploadFile, File, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.database import get_db
from app.models.store import Store
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.connectors.csv_connector import CSVConnector
from app.schemas.upload import UploadResponse

router = APIRouter()
connector = CSVConnector()


@router.post("/csv", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(..., description="Arquivo CSV ou XLSX"),
    data_type: str = Query(
        ..., 
        description="Tipo de dados: 'products' ou 'sales'",
        pattern="^(products|sales)$"
    ),
    store_id: int = Query(..., description="ID da loja"),
    db: AsyncSession = Depends(get_db),
):
    """
    Importa dados de produtos ou vendas a partir de um arquivo CSV/XLSX.

    - **products**: Importa/atualiza catálogo de produtos (upsert por EAN)
    - **sales**: Importa histórico de vendas (insere novos cupons)
    """
    # Verificar se a loja existe
    store = await db.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Loja com ID {store_id} não encontrada")

    # Validar tipo de arquivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo não fornecido")
    
    allowed_extensions = (".csv", ".xlsx", ".xls")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
        )

    # Ler conteúdo do arquivo
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    logger.info(f"Upload recebido: {file.filename} ({len(content)} bytes) - tipo: {data_type}")

    if data_type == "products":
        return await _import_products(db, store_id, content, file.filename)
    else:
        return await _import_sales(db, store_id, content, file.filename)


async def _import_products(
    db: AsyncSession, store_id: int, content: bytes, filename: str
) -> UploadResponse:
    """Importa produtos via CSV. Faz UPSERT por EAN."""
    products, errors = connector.parse_products_file(content, filename)
    
    imported = 0
    skipped = 0

    for product_data in products:
        # Verificar se produto já existe (por EAN + store_id)
        result = await db.execute(
            select(Product).where(
                Product.ean == product_data.ean,
                Product.store_id == store_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # UPDATE: atualiza campos do produto existente
            for field, value in product_data.model_dump(exclude_none=True).items():
                setattr(existing, field, value)
            imported += 1
        else:
            # INSERT: cria novo produto
            new_product = Product(
                store_id=store_id,
                **product_data.model_dump()
            )
            db.add(new_product)
            imported += 1

    await db.commit()
    logger.info(f"Produtos importados: {imported}, ignorados: {skipped}")

    return UploadResponse(
        success=True,
        data_type="products",
        records_imported=imported,
        records_skipped=skipped,
        errors=errors,
        message=f"✅ {imported} produtos importados com sucesso!"
    )


async def _import_sales(
    db: AsyncSession, store_id: int, content: bytes, filename: str
) -> UploadResponse:
    """Importa vendas via CSV. Pula cupons duplicados."""
    sales_data, errors = connector.parse_sales_file(content, filename)

    imported = 0
    skipped = 0

    for sale_data in sales_data:
        # Verificar se o cupom já existe
        result = await db.execute(
            select(Sale).where(
                Sale.sale_id == sale_data.sale_id,
                Sale.store_id == store_id
            )
        )
        if result.scalar_one_or_none():
            skipped += 1
            continue

        # Criar Sale
        sale = Sale(
            store_id=store_id,
            sale_id=sale_data.sale_id,
            timestamp=sale_data.timestamp,
            total=sale_data.total,
            payment_method=sale_data.payment_method,
        )
        db.add(sale)
        await db.flush()  # Gera o ID da sale

        # Criar SaleItems
        for item_data in sale_data.items:
            # Buscar product_id pelo EAN
            result = await db.execute(
                select(Product.id).where(
                    Product.ean == item_data.product_ean,
                    Product.store_id == store_id
                )
            )
            product_id = result.scalar_one_or_none()

            if product_id:
                sale_item = SaleItem(
                    sale_id_fk=sale.id,
                    product_id=product_id,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    discount=item_data.discount,
                )
                db.add(sale_item)
            else:
                errors.append(
                    f"Cupom {sale_data.sale_id}: Produto EAN '{item_data.product_ean}' não encontrado"
                )

        imported += 1

    await db.commit()
    logger.info(f"Vendas importadas: {imported}, duplicatas ignoradas: {skipped}")

    return UploadResponse(
        success=True,
        data_type="sales",
        records_imported=imported,
        records_skipped=skipped,
        errors=errors,
        message=f"✅ {imported} vendas importadas! ({skipped} duplicatas ignoradas)"
    )
