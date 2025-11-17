"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/health/database")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check."""
    try:
        # Simple query to test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@router.get("/health/config")
async def config_health_check():
    """Configuration health check."""
    return {
        "status": "healthy",
        "config": {
            "has_aws_credentials": settings.has_aws_credentials,
            "has_sqs_queue": settings.has_sqs_queue,
            "has_slack_webhook": settings.has_slack_webhook,
            "has_amazon_credentials": settings.has_amazon_credentials,
            "worker_enabled": settings.worker_enabled,
        },
    }

