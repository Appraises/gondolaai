from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Resposta do endpoint de upload."""
    success: bool
    data_type: str  # "products" ou "sales"
    records_imported: int
    records_skipped: int
    errors: list[str] = []
    message: str
