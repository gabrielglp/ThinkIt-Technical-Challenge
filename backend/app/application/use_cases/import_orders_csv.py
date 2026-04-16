import io
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from app.core.storage import upload_bytes
from etl.loader import load
from etl.transformer import transform
from etl.validators import validate_row


@dataclass
class ImportReport:
    s3_key: str
    valid_rows: int
    invalid_rows: int
    errors: list[str]
    customers_upserted: int
    products_upserted: int
    orders_upserted: int
    order_items_inserted: int


class S3UploadError(Exception):
    pass


class InvalidCsvError(Exception):
    pass


class NoValidRowsError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Nenhuma linha válida.")


class ImportOrdersCsvUseCase:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    async def execute(self, filename: str, content: bytes) -> ImportReport:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        safe_name = filename.replace(" ", "_")
        s3_key = f"csv-imports/{timestamp}_{uuid.uuid4().hex[:8]}_{safe_name}"

        try:
            upload_bytes(s3_key, content)
        except Exception as exc:
            raise S3UploadError() from exc

        try:
            df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
        except Exception as exc:
            raise InvalidCsvError() from exc

        raw_rows = df.to_dict(orient="records")
        valid_rows = []
        errors: list[str] = []
        for i, row in enumerate(raw_rows, start=2):
            validated, error = validate_row(row, i)
            if validated:
                valid_rows.append(validated)
            elif error:
                errors.append(error)

        if not valid_rows:
            raise NoValidRowsError(errors)

        entities = transform(valid_rows)

        with self._session_factory() as session:
            with session.begin():
                etl_report = load(session, entities)

        return ImportReport(
            s3_key=s3_key,
            valid_rows=len(valid_rows),
            invalid_rows=len(errors),
            errors=errors,
            customers_upserted=etl_report.customers_upserted,
            products_upserted=etl_report.products_upserted,
            orders_upserted=etl_report.orders_upserted,
            order_items_inserted=etl_report.order_items_inserted,
        )
