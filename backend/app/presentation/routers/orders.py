from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.use_cases.get_order_by_id import GetOrderByIdUseCase
from app.application.use_cases.list_orders import ListOrdersUseCase
from app.domain.value_objects import OrderFilters, OrderStatus, Pagination
from app.presentation.dependencies import get_list_orders_use_case, get_order_by_id_use_case
from app.presentation.schemas.order_schemas import OrderDetailSchema, OrderItemSchema, PaginatedOrdersSchema, OrderSchema, CustomerSchema

router = APIRouter()


@router.get("", response_model=PaginatedOrdersSchema)
async def list_orders(
    status: OrderStatus | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    min_value: Decimal | None = Query(None, ge=0),
    max_value: Decimal | None = Query(None, ge=0),
    customer_name: str | None = Query(None, max_length=255),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    use_case: ListOrdersUseCase = Depends(get_list_orders_use_case),
) -> PaginatedOrdersSchema:
    filters = OrderFilters(
        status=status,
        date_from=date_from,
        date_to=date_to,
        min_value=min_value,
        max_value=max_value,
        customer_name=customer_name,
    )
    pagination = Pagination(page=page, page_size=page_size)
    result = await use_case.execute(filters, pagination)

    return PaginatedOrdersSchema(
        items=[
            OrderSchema(
                order_id=o.order_id,
                customer_id=o.customer_id,
                customer_name=o.customer_name,
                status=o.status,
                created_at=o.created_at,
                updated_at=o.updated_at,
                total_amount=float(o.total_amount),
            )
            for o in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        has_next=result.has_next,
        has_previous=result.has_previous,
    )


@router.get("/{order_id}", response_model=OrderDetailSchema)
async def get_order(
    order_id: str,
    use_case: GetOrderByIdUseCase = Depends(get_order_by_id_use_case),
) -> OrderDetailSchema:
    order = await use_case.execute(order_id)

    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido '{order_id}' não encontrado.")

    return OrderDetailSchema(
        order_id=order.order_id,
        customer=CustomerSchema(
            customer_id=order.customer.customer_id,
            customer_name=order.customer.customer_name,
            customer_email=order.customer.customer_email,
            city=order.customer.city,
            state=order.customer.state,
        ),
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemSchema(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                category=item.category,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                discount_pct=float(item.discount_pct),
                total_price=float(item.total_price),
            )
            for item in order.items
        ],
        total_amount=float(order.total_amount),
    )
