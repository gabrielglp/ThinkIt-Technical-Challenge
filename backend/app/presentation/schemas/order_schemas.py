from datetime import datetime

from pydantic import BaseModel, ConfigDict

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
