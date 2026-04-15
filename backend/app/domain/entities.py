from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.value_objects import OrderStatus


@dataclass(frozen=True)
class Customer:
    customer_id: str
    customer_name: str
    customer_email: str
    city: str | None
    state: str | None


@dataclass(frozen=True)
class Product:
    product_id: str
    product_name: str
    category: str


@dataclass(frozen=True)
class OrderItem:
    id: str
    order_id: str
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_price: Decimal
    discount_pct: Decimal
    total_price: Decimal


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    customer_name: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    total_amount: Decimal


@dataclass(frozen=True)
class OrderDetail:
    order_id: str
    customer: Customer
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItem]
    total_amount: Decimal


@dataclass(frozen=True)
class TopProduct:
    product_id: str
    product_name: str
    category: str
    total_revenue: Decimal
    total_quantity: int


@dataclass(frozen=True)
class StatusCount:
    status: OrderStatus
    count: int


@dataclass(frozen=True)
class Metrics:
    average_ticket: Decimal
    top_products: list[TopProduct]
    orders_by_status: list[StatusCount]
    total_orders: int
    total_revenue: Decimal
