import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from etl.loader import load
from etl.transformer import transform
from etl.validators import ValidatedRow, validate_row

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl")

_ERROR_LOG = Path("etl_errors.log")


def _setup_error_log() -> None:
    _ERROR_LOG.write_text(
        f"# ETL error log — {datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )


def _log_error(msg: str) -> None:
    log.warning(msg)
    with _ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def _read_csv(csv_path: Path) -> list[dict]:
    log.info("Lendo CSV: %s", csv_path)
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    log.info("Total de linhas: %d", len(df))
    return df.to_dict(orient="records")


def _validate_all(raw_rows: list[dict]) -> tuple[list[ValidatedRow], list[str]]:
    valid: list[ValidatedRow] = []
    errors: list[str] = []

    for i, row in enumerate(raw_rows, start=2):  # start=2 porque linha 1 é o header
        validated, error = validate_row(row, line_number=i)
        if validated:
            valid.append(validated)
        else:
            errors.append(error)  # type: ignore[arg-type]

    return valid, errors


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL_SYNC")
    if not url:
        try:
            from app.core.config import settings
            url = settings.database_url_sync
        except Exception:
            pass
    if not url:
        raise RuntimeError("DATABASE_URL_SYNC não definida.")
    return url


def run(csv_path: Path) -> None:
    started_at = datetime.now(timezone.utc)
    _setup_error_log()

    raw_rows = _read_csv(csv_path)

    log.info("Validando linhas...")
    valid_rows, errors = _validate_all(raw_rows)

    for err in errors:
        _log_error(err)

    log.info("%d válidas | %d inválidas", len(valid_rows), len(errors))

    if not valid_rows:
        log.error("Nenhuma linha válida. Abortando.")
        sys.exit(1)

    log.info("Transformando entidades...")
    entities = transform(valid_rows)

    engine = create_engine(_get_database_url(), echo=False)

    log.info("Carregando no banco...")
    with Session(engine) as session:
        with session.begin():
            report = load(session, entities)

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()

    summary = {
        "status": "success",
        "csv_path": str(csv_path),
        "total_csv_rows": len(raw_rows),
        "valid_rows": len(valid_rows),
        "invalid_rows": len(errors),
        "customers_upserted": report.customers_upserted,
        "products_upserted": report.products_upserted,
        "orders_upserted": report.orders_upserted,
        "order_items_inserted": report.order_items_inserted,
        "elapsed_seconds": round(elapsed, 2),
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }

    log.info("ETL concluído em %.2fs", elapsed)
    log.info("customers=%d products=%d orders=%d items=%d",
             report.customers_upserted, report.products_upserted,
             report.orders_upserted, report.order_items_inserted)

    Path("etl_report.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m etl.load_orders <caminho_do_csv>", file=sys.stderr)
        sys.exit(1)

    csv_file = Path(sys.argv[1])

    if not csv_file.exists():
        print(f"Arquivo não encontrado: {csv_file}", file=sys.stderr)
        sys.exit(1)

    if csv_file.suffix.lower() != ".csv":
        print(f"Arquivo não é um CSV: {csv_file}", file=sys.stderr)
        sys.exit(1)

    run(csv_file)
