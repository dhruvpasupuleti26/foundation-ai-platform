"""Configuration schemas."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, computed_field


class PlatformMetadataConfig(BaseModel):
    name: str = "foundation-ai-platform"
    environment: str = "development"


class GatewayConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    enable_metrics: bool = True


class DatabaseConfig(BaseModel):
    engine: str = "sqlite"
    path: str = "./data/platform.db"
    host: str = "localhost"
    port: int | None = None
    database: str = "llm_platform"
    username: str | None = None
    password: str | None = None
    driver: str | None = None
    url: str | None = None
    echo: bool = False

    @computed_field
    @property
    def sqlalchemy_url(self) -> str:
        if self.url:
            return self.url

        engine = self.engine.lower()
        if engine == "sqlite":
            return f"sqlite+pysqlite:///{Path(self.path)}"
        if engine in {"postgres", "postgresql"}:
            driver = self.driver or "psycopg"
            port = self.port or 5432
            credentials = ""
            if self.username:
                credentials = self.username
                if self.password:
                    credentials = f"{credentials}:{self.password}"
                credentials = f"{credentials}@"
            return f"postgresql+{driver}://{credentials}{self.host}:{port}/{self.database}"
        if engine == "mysql":
            driver = self.driver or "pymysql"
            port = self.port or 3306
            credentials = ""
            if self.username:
                credentials = self.username
                if self.password:
                    credentials = f"{credentials}:{self.password}"
                credentials = f"{credentials}@"
            return f"mysql+{driver}://{credentials}{self.host}:{port}/{self.database}"
        raise ValueError(f"Unsupported database engine: {self.engine}")


class PluginConfig(BaseModel):
    enabled: list[str] = Field(default_factory=list)


class ServingConfig(BaseModel):
    default_engine: str = "vllm"
    supported_engines: list[str] = Field(default_factory=lambda: ["vllm", "huggingface-transformers"])


class TelemetrySinkConfig(BaseModel):
    enabled: bool = False


class TelemetryConfig(BaseModel):
    provider: str = "database"
    prometheus: TelemetrySinkConfig = Field(default_factory=lambda: TelemetrySinkConfig(enabled=True))
    opentelemetry: TelemetrySinkConfig = Field(default_factory=TelemetrySinkConfig)


class PlatformConfig(BaseModel):
    platform: PlatformMetadataConfig = Field(default_factory=PlatformMetadataConfig)
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    serving: ServingConfig = Field(default_factory=ServingConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
