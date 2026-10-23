from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pymongo.errors import ConnectionFailure
import redis

from app.core.config import settings
from app.core.databases import get_db, mongo_db, redis_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-throughput, asynchronous quantitative risk engine for FX & Interest Rate derivatives.",
    version="1.0.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)


@app.get("/")
def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}",
        "docs": f"Navigate to {settings.API_V1_STR}/docs for interactive API documentation.",
    }


@app.get(f"{settings.API_V1_STR}/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check verifying PostgreSQL, MongoDB, and Redis connections."""
    health_status = {
        "status": "healthy",
        "services": {
            "postgresql": "unhealthy",
            "mongodb": "unhealthy",
            "redis": "unhealthy",
        },
    }

    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["postgresql"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["postgresql"] = f"error: {str(e)}"

    try:
        mongo_db.command("ping")
        health_status["services"]["mongodb"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["mongodb"] = f"error: {str(e)}"

    try:
        if redis_client.ping():
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["status"] = "degraded"
            health_status["services"]["redis"] = "error: ping failed"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["redis"] = f"error: {str(e)}"

    if health_status["status"] == "degraded":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status