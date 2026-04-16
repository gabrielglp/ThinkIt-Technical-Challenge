from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order_by_id import GetOrderByIdUseCase
from app.application.use_cases.import_orders_csv import (
    ImportOrdersCsvUseCase,
    InvalidCsvError,
    NoValidRowsError,
    S3UploadError,
)
from app.application.use_cases.list_orders import ListOrdersUseCase
from app.application.use_cases.update_order import UpdateOrderUseCase
from app.domain.entities import User
from app.domain.value_objects import OrderFilters, OrderItemPayload, OrderStatus, OrderWritePayload, Pagination
from app.presentation.dependencies import (
    get_create_order_use_case,
    get_current_user,
    get_import_orders_csv_use_case,
    get_list_orders_use_case,
    get_order_by_id_use_case,
    get_update_order_use_case,
)
from app.presentation.schemas.order_schemas import (
    OrderDetailSchema,
    OrderSchema,
    OrderWriteSchema,
    PaginatedOrdersSchema,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedOrdersSchema,
    summary="Listar pedidos",
    description="Retorna uma lista paginada de pedidos com suporte a filtros por status, data, valor e nome do cliente.",
    responses={
        200: {"description": "Lista paginada de pedidos."},
        422: {"description": "Parâmetros de filtro inválidos."},
    },
)
async def list_orders(
    status: OrderStatus | None = Query(None, description="Filtrar por status do pedido"),
    date_from: datetime | None = Query(None, description="Data inicial (inclusive)"),
    date_to: datetime | None = Query(None, description="Data final (inclusive)"),
    min_value: Decimal | None = Query(None, ge=0, description="Valor mínimo do pedido"),
    max_value: Decimal | None = Query(None, ge=0, description="Valor máximo do pedido"),
    customer_name: str | None = Query(None, max_length=255, description="Busca parcial por nome do cliente"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página (máx. 100)"),
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
        items=[OrderSchema.model_validate(o) for o in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        has_next=result.has_next,
        has_previous=result.has_previous,
    )


@router.post(
    "",
    response_model=OrderDetailSchema,
    status_code=201,
    summary="Criar pedido",
    description="Cria um novo pedido. Requer autenticação JWT. O `order_id` é gerado automaticamente no formato `ORD-NNNNN`.",
    responses={
        201: {"description": "Pedido criado com sucesso."},
        401: {"description": "Token ausente ou inválido."},
        422: {"description": "Dados do pedido inválidos."},
    },
)
async def create_order(
    body: OrderWriteSchema,
    _: User = Depends(get_current_user),
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> OrderDetailSchema:
    order = await use_case.execute(_schema_to_payload(body))
    return OrderDetailSchema.model_validate(order)


@router.get(
    "/{order_id}",
    response_model=OrderDetailSchema,
    summary="Buscar pedido por ID",
    description="Retorna os detalhes completos de um pedido, incluindo dados do cliente e itens.",
    responses={
        200: {"description": "Detalhes do pedido."},
        404: {"description": "Pedido não encontrado."},
        422: {"description": "Formato de ID inválido (esperado: ORD-NNNNN)."},
    },
)
async def get_order(
    order_id: str = Path(..., pattern=r"^ORD-\d+$", description="ID do pedido (ex: ORD-00756)"),
    use_case: GetOrderByIdUseCase = Depends(get_order_by_id_use_case),
) -> OrderDetailSchema:
    order = await use_case.execute(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido '{order_id}' não encontrado.")
    return OrderDetailSchema.model_validate(order)


@router.put(
    "/{order_id}",
    response_model=OrderDetailSchema,
    summary="Atualizar pedido",
    description="Atualiza os dados de um pedido existente. Requer autenticação JWT. Os itens são substituídos integralmente.",
    responses={
        200: {"description": "Pedido atualizado com sucesso."},
        401: {"description": "Token ausente ou inválido."},
        404: {"description": "Pedido não encontrado."},
        422: {"description": "Dados inválidos ou formato de ID incorreto."},
    },
)
async def update_order(
    body: OrderWriteSchema,
    order_id: str = Path(..., pattern=r"^ORD-\d+$", description="ID do pedido (ex: ORD-00756)"),
    _: User = Depends(get_current_user),
    use_case: UpdateOrderUseCase = Depends(get_update_order_use_case),
) -> OrderDetailSchema:
    order = await use_case.execute(order_id, _schema_to_payload(body))
    if not order:
        raise HTTPException(status_code=404, detail=f"Pedido '{order_id}' não encontrado.")
    return OrderDetailSchema.model_validate(order)


@router.post(
    "/import",
    status_code=200,
    summary="Importar pedidos via CSV",
    description=(
        "Faz upload do `.csv` para o bucket S3, processa os pedidos de forma idempotente (upsert) "
        "e retorna relatório com contagem de registros válidos, inválidos, erros por linha e a chave S3 do arquivo salvo. "
        "Requer autenticação JWT."
    ),
    responses={
        200: {"description": "Importação concluída. Relatório com válidos, inválidos, erros e s3_key."},
        401: {"description": "Token ausente ou inválido."},
        422: {"description": "Arquivo inválido, não-CSV ou nenhuma linha processável."},
        500: {"description": "Falha ao fazer upload para o S3."},
    },
)
async def import_orders_csv(
    file: UploadFile = File(..., description="Arquivo .csv com os pedidos"),
    _: User = Depends(get_current_user),
    use_case: ImportOrdersCsvUseCase = Depends(get_import_orders_csv_use_case),
) -> dict[str, object]:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Envie um arquivo .csv válido.")

    content = await file.read()

    try:
        report = await use_case.execute(file.filename, content)
    except S3UploadError:
        raise HTTPException(status_code=500, detail="Falha ao fazer upload do CSV para o S3.")
    except InvalidCsvError:
        raise HTTPException(status_code=422, detail="Não foi possível ler o CSV.")
    except NoValidRowsError as exc:
        raise HTTPException(status_code=422, detail={"message": "Nenhuma linha válida.", "errors": exc.errors})

    return {
        "s3_key": report.s3_key,
        "valid_rows": report.valid_rows,
        "invalid_rows": report.invalid_rows,
        "errors": report.errors,
        "customers_upserted": report.customers_upserted,
        "products_upserted": report.products_upserted,
        "orders_upserted": report.orders_upserted,
        "order_items_inserted": report.order_items_inserted,
    }


def _schema_to_payload(body: OrderWriteSchema) -> OrderWritePayload:
    return OrderWritePayload(
        customer_id=body.customer_id,
        customer_name=body.customer_name,
        customer_email=str(body.customer_email),
        city=body.city,
        state=body.state,
        status=body.status,
        created_at=body.created_at,
        updated_at=body.updated_at,
        items=[
            OrderItemPayload(
                product_id=i.product_id,
                product_name=i.product_name,
                category=i.category,
                quantity=i.quantity,
                unit_price=i.unit_price,
                discount_pct=i.discount_pct,
            )
            for i in body.items
        ],
    )
