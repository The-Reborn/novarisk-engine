from motor.motor_asyncio import AsyncIOMotorClient
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to provide a SQL database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates all database tables defined in SQLAlchemy models."""
    from app.models.trade import Trade
    Base.metadata.create_all(bind=engine)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

def connect_to_mongo():
    """Connect to MongoDB on application startup,"""
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
    mongodb.db = mongodb.client.get_database(settings.MONGO_DB_NAME)

def close_mongo_connection():
    """Close MongoDB connection on application shutdown"""
    if mongodb.client:
        mongodb.client.close()


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


def get_redis():
    """Dependency to access the Redis cache instance."""
    return redis_client