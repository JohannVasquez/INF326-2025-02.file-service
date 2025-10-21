from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "servicio-archivos"
    app_env: str = "local"
    app_port: int = 8080

    postgres_host: str = Field("db", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field("filesvc", alias="POSTGRES_DB")
    postgres_user: str = Field("filesvc", alias="POSTGRES_USER")
    postgres_password: str = Field("filesvc", alias="POSTGRES_PASSWORD")

    minio_endpoint: str = Field("minio:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field("minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field("minioadmin", alias="MINIO_SECRET_KEY")
    minio_secure: bool = Field(False, alias="MINIO_SECURE")
    minio_bucket: str = Field("files", alias="MINIO_BUCKET")
    public_minio_url: str = Field("http://localhost:9000", alias="PUBLIC_MINIO_URL")


    rabbitmq_host: str = Field("rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field("guest", alias="RABBITMQ_USER")
    rabbitmq_password: str = Field("guest", alias="RABBITMQ_PASSWORD")
    rabbitmq_exchange: str = Field("files", alias="RABBITMQ_EXCHANGE")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
