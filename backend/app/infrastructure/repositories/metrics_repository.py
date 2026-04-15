from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Metrics, StatusCount, TopProduct
from app.domain.value_objects import OrderStatus


class SQLAlchemyMetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_metrics(self) -> Metrics:
        avg_row = (await self._session.execute(text("""
            SELECT
                COUNT(*)                        AS total_orders,
                COALESCE(SUM(order_total), 0)   AS total_revenue,
                COALESCE(AVG(order_total), 0)   AS average_ticket
            FROM (
                SELECT order_id, SUM(total_price) AS order_total
                FROM order_items
                GROUP BY order_id
            ) t
        """))).mappings().one()

        top_rows = (await self._session.execute(text("""
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                SUM(oi.total_price) AS total_revenue,
                SUM(oi.quantity)    AS total_quantity
            FROM order_items oi
            JOIN products p ON p.product_id = oi.product_id
            GROUP BY p.product_id, p.product_name, p.category
            ORDER BY total_revenue DESC
            LIMIT 5
        """))).mappings().all()

        status_rows = (await self._session.execute(text("""
            SELECT status, COUNT(*) AS count
            FROM orders
            GROUP BY status
        """))).mappings().all()

        top_products = [
            TopProduct(
                product_id=row["product_id"],
                product_name=row["product_name"],
                category=row["category"],
                total_revenue=Decimal(str(row["total_revenue"])),
                total_quantity=int(row["total_quantity"]),
            )
            for row in top_rows
        ]

        orders_by_status = [
            StatusCount(status=OrderStatus(row["status"]), count=int(row["count"]))
            for row in status_rows
        ]

        return Metrics(
            average_ticket=Decimal(str(avg_row["average_ticket"])).quantize(Decimal("0.01")),
            top_products=top_products,
            orders_by_status=orders_by_status,
            total_orders=int(avg_row["total_orders"]),
            total_revenue=Decimal(str(avg_row["total_revenue"])).quantize(Decimal("0.01")),
        )
