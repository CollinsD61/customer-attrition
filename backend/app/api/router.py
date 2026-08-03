from fastapi import APIRouter

from backend.app.api import auth, customers, dashboard, health, history, predict

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(predict.router, prefix="/predict", tags=["predict"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
