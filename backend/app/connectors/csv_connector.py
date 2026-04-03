"""
CSV/XLSX Connector — Adapter Pattern (Tier 3)

Lê planilhas exportadas de qualquer ERP e converte para o modelo canônico
do Gôndola.ai. Suporta nomes de colunas em português e inglês.

Conforme implementation_plan.md (Seção 4, Tier 3):
"O supermercado exporta um CSV/XLSX diário e faz upload no painel do Gôndola.ai"
"""

import io
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd
from loguru import logger

from app.schemas.product import ProductCreate
from app.schemas.sale import SaleCreate, SaleItemCreate


class CSVConnector:
    """
    Conector plug-and-play para planilhas CSV/XLSX.
    Aceita variações de nomes de colunas (pt-BR, en-US, abreviações comuns).
    """

    # Mapeamento flexível: nome canônico → possíveis nomes no CSV
    PRODUCT_COLUMN_MAP = {
        "ean": ["ean", "ean13", "codigo_barras", "cod_barras", "barcode", "codigo", "cod"],
        "name": ["nome", "descricao", "desc", "produto", "name", "description", "item"],
        "category": ["categoria", "secao", "departamento", "category", "dept", "setor"],
        "unit_price": ["preco", "preco_venda", "price", "valor", "pv", "preco_unitario"],
        "cost_price": ["custo", "preco_custo", "cost", "pc", "custo_unitario"],
        "stock_qty": ["estoque", "quantidade", "stock", "qty", "saldo", "qtd"],
        "expiry_date": ["validade", "data_validade", "expiry", "vencimento", "dt_validade"],
        "supplier": ["fornecedor", "supplier", "fabricante"],
        "external_id": ["id", "id_produto", "codigo_interno", "external_id", "cod_interno"],
    }

    SALE_COLUMN_MAP = {
        "sale_id": ["cupom", "venda", "nf", "nota", "sale_id", "transaction_id", "id_venda"],
        "timestamp": ["data", "data_hora", "timestamp", "date", "dt_venda", "data_venda"],
        "product_ean": ["ean", "codigo_barras", "barcode", "produto_ean", "cod_barras"],
        "product_name": ["produto", "nome", "descricao", "item", "name"],
        "quantity": ["quantidade", "qtd", "qty", "quantity"],
        "unit_price": ["preco", "preco_unitario", "valor", "price", "pv"],
        "discount": ["desconto", "discount", "desc"],
        "total": ["total", "valor_total", "subtotal"],
        "payment_method": ["pagamento", "forma_pagamento", "payment", "tipo_pagamento"],
    }

    def parse_products_file(self, file_content: bytes, filename: str) -> tuple[list[ProductCreate], list[str]]:
        """
        Lê um arquivo de produtos (CSV ou XLSX) e retorna lista de ProductCreate.

        Returns:
            tuple: (lista de produtos validados, lista de erros/warnings)
        """
        df = self._read_file(file_content, filename)
        df = self._normalize_columns(df, self.PRODUCT_COLUMN_MAP)
        
        products = []
        errors = []

        for idx, row in df.iterrows():
            try:
                product = ProductCreate(
                    external_id=self._safe_str(row.get("external_id")),
                    ean=self._safe_str(row.get("ean", "")),
                    name=self._safe_str(row.get("name", "Sem Nome")),
                    category=self._safe_str(row.get("category", "Geral")),
                    unit_price=self._safe_decimal(row.get("unit_price", 0)),
                    cost_price=self._safe_decimal(row.get("cost_price")),
                    stock_qty=self._safe_int(row.get("stock_qty", 0)),
                    expiry_date=self._safe_date(row.get("expiry_date")),
                    supplier=self._safe_str(row.get("supplier")),
                )
                products.append(product)
            except Exception as e:
                errors.append(f"Linha {idx + 2}: {str(e)}")
                logger.warning(f"Erro ao parsear produto na linha {idx + 2}: {e}")

        logger.info(f"CSV Connector: {len(products)} produtos parseados, {len(errors)} erros")
        return products, errors

    def parse_sales_file(self, file_content: bytes, filename: str) -> tuple[list[SaleCreate], list[str]]:
        """
        Lê um arquivo de vendas (CSV ou XLSX) e retorna lista de SaleCreate.
        
        O CSV de vendas geralmente tem 1 linha por item vendido.
        Agrupamos pelo sale_id (cupom) para montar a estrutura Sale → SaleItems.
        """
        df = self._read_file(file_content, filename)
        df = self._normalize_columns(df, self.SALE_COLUMN_MAP)

        sales = []
        errors = []

        # Agrupar por cupom (sale_id)
        if "sale_id" not in df.columns:
            # Se não tem coluna de cupom, gerar um ID por linha
            df["sale_id"] = [f"AUTO_{i}" for i in range(len(df))]

        grouped = df.groupby("sale_id")

        for sale_id, group in grouped:
            try:
                items = []
                total = Decimal("0")

                for _, row in group.iterrows():
                    qty = self._safe_decimal(row.get("quantity", 1))
                    price = self._safe_decimal(row.get("unit_price", 0))
                    discount = self._safe_decimal(row.get("discount", 0))
                    item_total = (qty * price) - discount
                    total += item_total

                    items.append(SaleItemCreate(
                        product_ean=self._safe_str(row.get("product_ean", "")),
                        quantity=qty,
                        unit_price=price,
                        discount=discount,
                    ))

                # Pegar timestamp da primeira linha do grupo
                ts = self._safe_datetime(group.iloc[0].get("timestamp"))

                sale = SaleCreate(
                    sale_id=str(sale_id),
                    timestamp=ts or datetime.utcnow(),
                    total=self._safe_decimal(group.iloc[0].get("total")) or total,
                    payment_method=self._safe_str(group.iloc[0].get("payment_method")),
                    items=items,
                )
                sales.append(sale)
            except Exception as e:
                errors.append(f"Cupom {sale_id}: {str(e)}")
                logger.warning(f"Erro ao parsear venda {sale_id}: {e}")

        logger.info(f"CSV Connector: {len(sales)} vendas parseadas, {len(errors)} erros")
        return sales, errors

    # ── Funções auxiliares ──

    def _read_file(self, content: bytes, filename: str) -> pd.DataFrame:
        """Lê CSV ou XLSX a partir de bytes."""
        buffer = io.BytesIO(content)
        if filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(buffer)
        else:
            # Tenta diferentes encodings comuns no Brasil
            for encoding in ["utf-8", "latin-1", "cp1252"]:
                try:
                    buffer.seek(0)
                    return pd.read_csv(buffer, encoding=encoding, sep=None, engine="python")
                except UnicodeDecodeError:
                    continue
            raise ValueError("Não foi possível ler o arquivo. Encodings tentados: utf-8, latin-1, cp1252")

    def _normalize_columns(self, df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
        """
        Normaliza os nomes das colunas do DataFrame.
        Mapeia variações (pt-BR, en-US) para os nomes canônicos.
        """
        # Limpar: lowercase, strip, remover acentos simples
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("ç", "c")
            .str.replace("ã", "a")
            .str.replace("ê", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
        )

        # Mapear aliases para nomes canônicos
        rename_map = {}
        for canonical_name, aliases in column_map.items():
            for alias in aliases:
                if alias in df.columns and canonical_name not in df.columns:
                    rename_map[alias] = canonical_name
                    break

        df = df.rename(columns=rename_map)
        logger.debug(f"Colunas normalizadas: {list(df.columns)}, renomeadas: {rename_map}")
        return df

    @staticmethod
    def _safe_str(value) -> Optional[str]:
        if pd.isna(value) or value is None:
            return None
        return str(value).strip()

    @staticmethod
    def _safe_decimal(value) -> Optional[Decimal]:
        if pd.isna(value) or value is None:
            return None
        try:
            # Aceita formato brasileiro (vírgula) e internacional (ponto)
            cleaned = str(value).replace("R$", "").replace(" ", "").strip()
            if "," in cleaned and "." in cleaned:
                cleaned = cleaned.replace(".", "").replace(",", ".")
            elif "," in cleaned:
                cleaned = cleaned.replace(",", ".")
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def _safe_int(value) -> int:
        if pd.isna(value) or value is None:
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _safe_date(value) -> Optional[date]:
        if pd.isna(value) or value is None:
            return None
        try:
            if isinstance(value, date):
                return value
            return pd.to_datetime(value, dayfirst=True).date()
        except Exception:
            return None

    @staticmethod
    def _safe_datetime(value) -> Optional[datetime]:
        if pd.isna(value) or value is None:
            return None
        try:
            if isinstance(value, datetime):
                return value
            return pd.to_datetime(value, dayfirst=True).to_pydatetime()
        except Exception:
            return None
