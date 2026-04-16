from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.value_objects import OrderStatus


class CustomerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    customer_name: str
    customer_email: str
    city: str | None
    state: str | None


class OrderItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_price: float
    discount_pct: float
    total_price: float


class OrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer_id: str
    customer_name: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    total_amount: float


class OrderDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer: CustomerSchema
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemSchema]
    total_amount: float


class PaginatedOrdersSchema(BaseModel):
    items: list[OrderSchema]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# ── Write schemas ──────────────────────────────────────────────────────────────

class OrderItemWriteSchema(BaseModel):
    product_id: str = Field(..., pattern=r"^PROD-\d+$")
    product_name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1)
    unit_price: Decimal = Field(..., ge=0)
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class OrderWriteSchema(BaseModel):
    customer_id: str = Field(..., pattern=r"^CLI-\d+$")
    customer_name: str = Field(..., min_length=2, max_length=255)
    customer_email: EmailStr
    city: str | None = None
    state: str | None = Field(default=None, max_length=2)
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemWriteSchema] = Field(..., min_length=1)
