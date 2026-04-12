from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    app_name: str = "SyanaTek"
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "syanatek")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "12345678")
    db_connect_retries: int = int(os.getenv("DB_CONNECT_RETRIES", "3"))
    db_retry_delay_s: int = int(os.getenv("DB_RETRY_DELAY_S", "2"))
    asset_manifest: str = os.getenv("ASSET_MANIFEST", str(BASE_DIR / "assets" / "parts_manifest.json"))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
