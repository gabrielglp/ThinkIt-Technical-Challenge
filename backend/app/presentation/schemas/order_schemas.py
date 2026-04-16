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



class OrderItemWriteSchema(BaseModel):
    product_id: str = Field(..., pattern=r"^PROD-\d+$", examples=["PROD-00123"])
    product_name: str = Field(..., min_length=1, max_length=255, examples=["Tênis Esportivo"])
    category: str = Field(..., min_length=1, max_length=100, examples=["Esportes"])
    quantity: int = Field(..., ge=1, examples=[2])
    unit_price: Decimal = Field(..., ge=0, examples=[199.90])
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100, examples=[10.0])


class OrderWriteSchema(BaseModel):
    customer_id: str = Field(..., pattern=r"^CLI-\d+$", examples=["CLI-00456"])
    customer_name: str = Field(..., min_length=2, max_length=255, examples=["Maria Souza"])
    customer_email: EmailStr = Field(..., examples=["maria@email.com"])
    city: str | None = Field(default=None, examples=["São Paulo"])
    state: str | None = Field(default=None, max_length=2, examples=["SP"])
    status: OrderStatus = Field(..., examples=["processing"])
    created_at: datetime = Field(..., examples=["2024-06-01T10:00:00Z"])
    updated_at: datetime = Field(..., examples=["2024-06-01T10:00:00Z"])
    items: list[OrderItemWriteSchema] = Field(..., min_length=1)
