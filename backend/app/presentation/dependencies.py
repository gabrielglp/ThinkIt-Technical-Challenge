from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.get_metrics import GetMetricsUseCase
from app.application.use_cases.get_order_by_id import GetOrderByIdUseCase
from app.application.use_cases.list_orders import ListOrdersUseCase
from app.infrastructure.database import get_db_session
from app.infrastructure.repositories import SQLAlchemyMetricsRepository, SQLAlchemyOrderRepository


def get_list_orders_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> ListOrdersUseCase:
    return ListOrdersUseCase(SQLAlchemyOrderRepository(session))


def get_order_by_id_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> GetOrderByIdUseCase:
    return GetOrderByIdUseCase(SQLAlchemyOrderRepository(session))


def get_metrics_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> GetMetricsUseCase:
    return GetMetricsUseCase(SQLAlchemyMetricsRepository(session))
