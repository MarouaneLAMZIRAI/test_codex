from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text

from app.config import settings


def run_sql_file(engine, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    engine = create_engine(settings.database_url)
    run_sql_file(engine, root / "database" / "sql" / "001_schema.sql")
    run_sql_file(engine, root / "database" / "sql" / "002_seed_demo.sql")
    print("Database initialized.")
