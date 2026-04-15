import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

VALID_STATUSES = {"processing", "shipped", "delivered", "cancelled"}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ORDER_ID_RE = re.compile(r"^ORD-\d{4,6}$")
_CUSTOMER_ID_RE = re.compile(r"^CLI-\d{3,6}$")
_PRODUCT_ID_RE = re.compile(r"^PROD-\d{3,6}$")
_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class ValidatedRow:
    order_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_price: Decimal
    discount_pct: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    city: str | None
    state: str | None


def _clean(value: object) -> str | None:
    s = str(value).strip() if value is not None else ""
    return s if s else None


def validate_row(row: dict, line_number: int) -> tuple["ValidatedRow | None", "str | None"]:
    errors: list[str] = []

    order_id = _clean(row.get("order_id"))
    if not order_id:
        errors.append("order_id vazio")
    elif not _ORDER_ID_RE.match(order_id):
        errors.append(f"order_id inválido: '{order_id}'")

    customer_id = _clean(row.get("customer_id"))
    if not customer_id:
        errors.append("customer_id vazio")
    elif not _CUSTOMER_ID_RE.match(customer_id):
        errors.append(f"customer_id inválido: '{customer_id}'")

    product_id = _clean(row.get("product_id"))
    if not product_id:
        errors.append("product_id vazio")
    elif not _PRODUCT_ID_RE.match(product_id):
        errors.append(f"product_id inválido: '{product_id}'")

    customer_name = _clean(row.get("customer_name"))
    if not customer_name:
        errors.append("customer_name vazio")

    customer_email = _clean(row.get("customer_email"))
    if not customer_email:
        errors.append("customer_email vazio")
    elif not _EMAIL_RE.match(customer_email):
        errors.append(f"customer_email inválido: '{customer_email}'")

    product_name = _clean(row.get("product_name"))
    if not product_name:
        errors.append("product_name vazio")

    category = _clean(row.get("category"))
    if not category:
        errors.append("category vazia")

    quantity: int | None = None
    try:
        quantity = int(row.get("quantity", ""))
        if quantity <= 0:
            errors.append(f"quantity deve ser > 0, recebido: {quantity}")
    except (ValueError, TypeError):
        errors.append(f"quantity inválido: '{row.get('quantity')}'")

    unit_price: Decimal | None = None
    try:
        unit_price = Decimal(str(row.get("unit_price", "")).strip())
        if unit_price < 0:
            errors.append(f"unit_price deve ser >= 0, recebido: {unit_price}")
    except InvalidOperation:
        errors.append(f"unit_price inválido: '{row.get('unit_price')}'")

    discount_pct: Decimal | None = None
    try:
        discount_pct = Decimal(str(row.get("discount_pct", "0")).strip())
        if not (Decimal("0") <= discount_pct <= Decimal("100")):
            errors.append(f"discount_pct fora do intervalo [0,100]: {discount_pct}")
    except InvalidOperation:
        errors.append(f"discount_pct inválido: '{row.get('discount_pct')}'")

    status = _clean(row.get("status"))
    if not status:
        errors.append("status vazio")
    elif status not in VALID_STATUSES:
        errors.append(f"status inválido: '{status}'. Esperado: {VALID_STATUSES}")

    created_at: datetime | None = None
    raw_created = str(row.get("created_at", "")).strip()
    try:
        created_at = datetime.strptime(raw_created, _DATETIME_FMT)
    except ValueError:
        errors.append(f"created_at inválido: '{raw_created}'")

    updated_at: datetime | None = None
    raw_updated = str(row.get("updated_at", "")).strip()
    try:
        updated_at = datetime.strptime(raw_updated, _DATETIME_FMT)
    except ValueError:
        errors.append(f"updated_at inválido: '{raw_updated}'")

    if created_at and updated_at and updated_at < created_at:
        errors.append(f"updated_at ({updated_at}) anterior a created_at ({created_at})")

    city = _clean(row.get("city"))
    state_raw = _clean(row.get("state"))
    state = state_raw[:2].upper() if state_raw else None

    if errors:
        return None, f"Linha {line_number} [{row.get('order_id', '?')}]: {'; '.join(errors)}"

    return (
        ValidatedRow(
            order_id=order_id,  # type: ignore[arg-type]
            customer_id=customer_id,  # type: ignore[arg-type]
            customer_name=customer_name,  # type: ignore[arg-type]
            customer_email=customer_email,  # type: ignore[arg-type]
            product_id=product_id,  # type: ignore[arg-type]
            product_name=product_name,  # type: ignore[arg-type]
            category=category,  # type: ignore[arg-type]
            quantity=quantity,  # type: ignore[arg-type]
            unit_price=unit_price,  # type: ignore[arg-type]
            discount_pct=discount_pct,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            created_at=created_at,  # type: ignore[arg-type]
            updated_at=updated_at,  # type: ignore[arg-type]
            city=city,
            state=state,
        ),
        None,
    )
