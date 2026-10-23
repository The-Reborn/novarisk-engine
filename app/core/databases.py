from pymongo import MongoClient
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


mongo_client = MongoClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]


def get_mongo_db():
    """Dependency to access the MongoDB report database."""
    return mongo_db


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


def get_redis():
    """Dependency to access the Redis cache instance."""
    return redis_client