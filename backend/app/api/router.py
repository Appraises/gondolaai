from fastapi import APIRouter
from app.api.upload import router as upload_router
from app.api.products import router as products_router
from app.api.sales import router as sales_router
from app.api.features import router as features_router
from app.api.predictions import router as predictions_router
from app.api.alerts import router as alerts_router
from app.api.whatsapp import router as whatsapp_router
from app.api.pricing import router as pricing_router

api_router = APIRouter()

api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
api_router.include_router(products_router, prefix="/products", tags=["Produtos"])
api_router.include_router(sales_router, prefix="/sales", tags=["Vendas"])
api_router.include_router(features_router, prefix="/features", tags=["Features (ML)"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["Predições"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alertas"])
api_router.include_router(whatsapp_router, prefix="/whatsapp", tags=["WhatsApp/Evolution"])
api_router.include_router(pricing_router, prefix="/pricing", tags=["Pricing"])

