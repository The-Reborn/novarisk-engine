from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pymongo.errors import ConnectionFailure
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.databases import (
    get_db, init_db,
    connect_to_mongo, close_mongo_connection,
    redis_client
)
from app.api.market import router as market_router
from app.api.trades import router as trades_router
from app.api.pricing import router as pricing_router
from app.api.reports import router as reports_router
from app.api.risk import router as risk_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        connect_to_mongo()
        print("PostgreSQL and MongoDB connected successfully.")
    except Exception as e:
        print(f"Error during startup connection: {e}")
    yield

    close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-throughput, asynchronous quantitative risk engine for FX & Interest Rate derivatives.",
    version="1.0.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

app.include_router(market_router, prefix=settings.API_V1_STR)
app.include_router(trades_router, prefix=settings.API_V1_STR)
app.include_router(pricing_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)


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