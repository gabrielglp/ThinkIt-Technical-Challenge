from fastapi import APIRouter, Depends

from app.application.use_cases.get_metrics import GetMetricsUseCase
from app.presentation.dependencies import get_metrics_use_case
from app.presentation.schemas.metrics_schemas import MetricsSchema, StatusCountSchema, TopProductSchema

router = APIRouter()


@router.get("", response_model=MetricsSchema)
async def get_metrics(
    use_case: GetMetricsUseCase = Depends(get_metrics_use_case),
) -> MetricsSchema:
    metrics = await use_case.execute()

    return MetricsSchema(
        average_ticket=float(metrics.average_ticket),
        total_orders=metrics.total_orders,
        total_revenue=float(metrics.total_revenue),
        top_products=[TopProductSchema.model_validate(p) for p in metrics.top_products],
        orders_by_status=[StatusCountSchema.model_validate(s) for s in metrics.orders_by_status],
    )
