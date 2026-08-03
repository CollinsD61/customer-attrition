from fastapi import APIRouter

from backend.app.core.config import settings

router = APIRouter()


@router.get("")
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
