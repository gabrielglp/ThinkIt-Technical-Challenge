from pydantic import BaseModel

from app.domain.value_objects import OrderStatus


class TopProductSchema(BaseModel):
    product_id: str
    product_name: str
    category: str
    total_revenue: float
    total_quantity: int


class StatusCountSchema(BaseModel):
    status: OrderStatus
    count: int


class MetricsSchema(BaseModel):
    average_ticket: float
    total_orders: int
    total_revenue: float
    top_products: list[TopProductSchema]
    orders_by_status: list[StatusCountSchema]
