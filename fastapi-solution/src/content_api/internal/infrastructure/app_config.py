from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",
    )

    # Название проекта. Используется в Swagger-документации.
    project_name: str = Field("movies", validation_alias="PROJECT_NAME")

    # Настройки Redis.
    redis_host: str = Field("127.0.0.1", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")

    # Настройки Elasticsearch.
    elastic_host: str = Field("127.0.0.1", validation_alias="ELASTIC_HOST")
    elastic_port: int = Field(9200, validation_alias="ELASTIC_PORT")
    elastic_schema: str = Field("http://", validation_alias="ELASTIC_SCHEMA")

    # Настройки Auth gRPC.
    auth_grpc_host: str = Field("127.0.0.1", validation_alias="AUTH_GRPC_HOST")
    auth_grpc_port: int = Field(50051, validation_alias="AUTH_GRPC_PORT")
    auth_grpc_timeout_seconds: float = Field(
        0.3,
        validation_alias="AUTH_GRPC_TIMEOUT_SECONDS",
    )

    # Настройки формата логов.
    log_json: bool = Field(True, validation_alias="LOG_JSON")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    # Настройки OpenTelemetry (traces).
    otel_enabled: bool = Field(True, validation_alias="OTEL_ENABLED")
    otel_service_name: str = Field(
        "content-api",
        validation_alias="OTEL_SERVICE_NAME",
    )
    otel_service_version: str = Field(
        "0.1.0",
        validation_alias="OTEL_SERVICE_VERSION",
    )
    otel_environment: str = Field(
        "development",
        validation_alias="OTEL_ENVIRONMENT",
    )
    otel_exporter_otlp_endpoint: str = Field(
        "http://127.0.0.1:4317",
        validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT",
    )
    otel_exporter_otlp_insecure: bool = Field(
        True,
        validation_alias="OTEL_EXPORTER_OTLP_INSECURE",
    )

    @classmethod
    def from_env(cls, env_file: str) -> "Settings":
        env_path = Path(env_file)
        if not env_path.exists():
            raise FileNotFoundError(f"File {env_file} not found")

        if not env_path.is_file():
            raise ValueError(f"{env_file} is not a file")

        return cls(
            _env_file=str(env_path),
            _env_file_encoding="utf-8-sig",
        )
