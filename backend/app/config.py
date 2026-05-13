from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Security
    noc_api_bearer_token: str = "changeme"

    # Network
    tailscale_ip: str = "127.0.0.1"
    api_port: int = 8000
    cors_allowed_origins: str = "http://localhost"

    # SSH
    ssh_key_path: str = "/root/.ssh/noc_collector_ed25519"
    ssh_control_path: str = "~/.ssh/cm-%r@%h:%p"
    ssh_control_persist: str = "10m"

    # Storage
    sqlite_db_path: str = "/data/noc.db"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Polling intervals (seconds)
    poll_interval_http: int = 15
    poll_interval_metrics: int = 60
    poll_interval_docker: int = 60
    poll_interval_smtp: int = 60
    poll_interval_backups: int = 300
    poll_interval_deploys: int = 60
    poll_interval_ssl: int = 21600
    poll_interval_dns: int = 3600
    poll_interval_ptr: int = 21600

    # Cache
    cache_ttl_seconds: int = 5

    # Timeouts
    http_timeout_seconds: int = 5
    ssh_timeout_seconds: int = 10
    dns_timeout_seconds: int = 3

    # Servers — "hostname:display_name:provider:region" comma-separated
    servers_config: str = "vps-myrock:VPS-MyRock:Hetzner:nbg1"

    # DNS resolvers
    dns_resolvers: str = "1.1.1.1,8.8.8.8"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def dns_resolvers_list(self) -> list[str]:
        return [r.strip() for r in self.dns_resolvers.split(",") if r.strip()]


settings = Settings()
