from decimal import Decimal

import pytest

from etl.validators import ValidatedRow, validate_row

_VALID_ROW: dict = {
    "order_id": "ORD-00001",
    "customer_id": "CLI-001",
    "customer_name": "João Silva",
    "customer_email": "joao@example.com",
    "product_id": "PROD-001",
    "product_name": "Notebook Pro",
    "category": "Eletrônicos",
    "quantity": "2",
    "unit_price": "1500.00",
    "discount_pct": "10",
    "status": "delivered",
    "created_at": "2024-01-15 10:00:00",
    "updated_at": "2024-01-16 10:00:00",
    "city": "São Paulo",
    "state": "SP",
}


class TestValidateRowSuccess:
    def test_valid_row_returns_validated_row(self):
        result, error = validate_row(_VALID_ROW, 1)
        assert error is None
        assert isinstance(result, ValidatedRow)

    def test_parsed_types(self):
        result, _ = validate_row(_VALID_ROW, 1)
        assert result.quantity == 2
        assert result.unit_price == Decimal("1500.00")
        assert result.discount_pct == Decimal("10")

    def test_state_uppercased_and_truncated(self):
        row = {**_VALID_ROW, "state": "rj"}
        result, _ = validate_row(row, 1)
        assert result.state == "RJ"

    def test_missing_city_and_state_allowed(self):
        row = {**_VALID_ROW, "city": "", "state": ""}
        result, error = validate_row(row, 1)
        assert error is None
        assert result.city is None
        assert result.state is None

    def test_zero_discount_allowed(self):
        row = {**_VALID_ROW, "discount_pct": "0"}
        result, error = validate_row(row, 1)
        assert error is None
        assert result.discount_pct == Decimal("0")


class TestValidateRowFailures:
    def test_invalid_order_id_format(self):
        row = {**_VALID_ROW, "order_id": "ORDER-001"}
        result, error = validate_row(row, 2)
        assert result is None
        assert "order_id inválido" in error

    def test_missing_order_id(self):
        row = {**_VALID_ROW, "order_id": ""}
        result, error = validate_row(row, 3)
        assert result is None
        assert "order_id vazio" in error

    def test_invalid_customer_id_format(self):
        row = {**_VALID_ROW, "customer_id": "CUST-001"}
        result, error = validate_row(row, 4)
        assert result is None
        assert "customer_id inválido" in error

    def test_invalid_product_id_format(self):
        row = {**_VALID_ROW, "product_id": "PRD-001"}
        result, error = validate_row(row, 5)
        assert result is None
        assert "product_id inválido" in error

    def test_invalid_email(self):
        row = {**_VALID_ROW, "customer_email": "not-an-email"}
        result, error = validate_row(row, 6)
        assert result is None
        assert "customer_email inválido" in error

    def test_quantity_zero_rejected(self):
        row = {**_VALID_ROW, "quantity": "0"}
        result, error = validate_row(row, 7)
        assert result is None
        assert "quantity deve ser > 0" in error

    def test_quantity_negative_rejected(self):
        row = {**_VALID_ROW, "quantity": "-1"}
        result, error = validate_row(row, 8)
        assert result is None
        assert "quantity deve ser > 0" in error

    def test_discount_above_100_rejected(self):
        row = {**_VALID_ROW, "discount_pct": "101"}
        result, error = validate_row(row, 9)
        assert result is None
        assert "discount_pct fora do intervalo" in error

    def test_invalid_status(self):
        row = {**_VALID_ROW, "status": "pending"}
        result, error = validate_row(row, 10)
        assert result is None
        assert "status inválido" in error

    def test_updated_at_before_created_at(self):
        row = {**_VALID_ROW, "updated_at": "2024-01-14 10:00:00"}
        result, error = validate_row(row, 11)
        assert result is None
        assert "updated_at" in error and "anterior" in error

    def test_invalid_datetime_format(self):
        row = {**_VALID_ROW, "created_at": "2024/01/15"}
        result, error = validate_row(row, 12)
        assert result is None
        assert "created_at inválido" in error

    def test_error_includes_line_number(self):
        row = {**_VALID_ROW, "order_id": ""}
        _, error = validate_row(row, 42)
        assert "Linha 42" in error

    def test_all_statuses_valid(self):
        for status in ("processing", "shipped", "delivered", "cancelled"):
            row = {**_VALID_ROW, "status": status}
            result, error = validate_row(row, 1)
            assert error is None, f"Status '{status}' deveria ser válido"
