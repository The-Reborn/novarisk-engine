from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "NovaRisk Engine"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "novarisk_db"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # MongoDB Configuration
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "novarisk_reports"

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        case_sensitive = True


settings = Settings()