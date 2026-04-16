from pydantic import BaseModel, ConfigDict

from app.domain.value_objects import OrderStatus


class TopProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_name: str
    category: str
    total_revenue: float
    total_quantity: int


class StatusCountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: OrderStatus
    count: int


class MetricsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    average_ticket: float
    total_orders: int
    total_revenue: float
    top_products: list[TopProductSchema]
    orders_by_status: list[StatusCountSchema]
