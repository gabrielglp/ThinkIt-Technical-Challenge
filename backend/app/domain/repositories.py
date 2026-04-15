"""
Repository interfaces — contratos do domínio.
Uso de Protocol para inversão de dependência sem herança (SOLID: DIP).
A camada de infraestrutura implementa, a de aplicação depende somente desta interface.
"""

from typing import Protocol, runtime_checkable

from app.domain.entities import Metrics, Order, OrderDetail
from app.domain.value_objects import OrderFilters, Pagination, PaginatedResult


@runtime_checkable
class OrderRepository(Protocol):
    """Contrato de acesso a pedidos."""

    async def list_orders(
        self,
        filters: OrderFilters,
        pagination: Pagination,
    ) -> PaginatedResult[Order]:
        """Retorna lista paginada de pedidos aplicando os filtros fornecidos."""
        ...

    async def get_by_id(self, order_id: str) -> OrderDetail | None:
        """Retorna o detalhe completo de um pedido, incluindo itens e cliente."""
        ...


@runtime_checkable
class MetricsRepository(Protocol):
    """Contrato de acesso às métricas operacionais."""

    async def get_metrics(self) -> Metrics:
        """
        Retorna:
        - Ticket médio geral
        - Top 5 produtos por receita
        - Contagem de pedidos por status
        - Total de pedidos
        - Receita total
        """
        ...
