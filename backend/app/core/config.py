from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_version: str = "0.1.0"

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "pyorchestrator"
    postgres_user: str = "pyorch"
    postgres_password: str = "pyorch_secret"

    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "pyorchestrator"
    minio_secure: bool = False

    secret_master_key: str = "change-me-in-production-32chars!!"
    jwt_secret: str = "jwt-dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"

    runtime_queue_key: str = "runtime:jobs"
    internal_api_key: str = "internal-dev-key"
    scheduler_reload_channel: str = "scheduler:reload"
    script_updated_channel: str = "script:updated"

    default_admin_email: str = "admin@pyorchestrator.local"
    default_admin_password: str = "admin"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
