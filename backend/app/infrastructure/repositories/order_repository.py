import uuid
from decimal import Decimal

from sqlalchemy import Numeric, String, bindparam, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Customer, Order, OrderDetail, OrderItem
from app.domain.value_objects import OrderFilters, OrderStatus, OrderWritePayload, Pagination, PaginatedResult

_LIST_ORDERS_SQL = text("""
    WITH order_totals AS (
        SELECT
            o.order_id,
            o.customer_id,
            c.customer_name,
            o.status,
            o.created_at,
            o.updated_at,
            COALESCE(SUM(oi.total_price), 0) AS total_amount
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        LEFT JOIN order_items oi ON oi.order_id = o.order_id
        WHERE
            (:status IS NULL OR o.status = :status)
            AND (:date_from IS NULL OR o.created_at >= :date_from)
            AND (:date_to IS NULL OR o.created_at <= :date_to)
            AND (:customer_name_pattern IS NULL OR c.customer_name ILIKE :customer_name_pattern)
        GROUP BY o.order_id, o.customer_id, c.customer_name, o.status, o.created_at, o.updated_at
        HAVING
            (:min_value IS NULL OR COALESCE(SUM(oi.total_price), 0) >= :min_value)
            AND (:max_value IS NULL OR COALESCE(SUM(oi.total_price), 0) <= :max_value)
    )
    SELECT *, COUNT(*) OVER() AS total_count
    FROM order_totals
    ORDER BY created_at DESC
    LIMIT :limit OFFSET :offset
""").bindparams(
    bindparam("status", type_=String),
    bindparam("date_from", type_=TIMESTAMP(timezone=True)),
    bindparam("date_to", type_=TIMESTAMP(timezone=True)),
    bindparam("customer_name_pattern", type_=String),
    bindparam("min_value", type_=Numeric),
    bindparam("max_value", type_=Numeric),
)


class SQLAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(
        self,
        filters: OrderFilters,
        pagination: Pagination,
    ) -> PaginatedResult[Order]:
        params: dict[str, object] = {
            "status": filters.status.value if filters.status else None,
            "date_from": filters.date_from,
            "date_to": filters.date_to,
            "customer_name_pattern": f"%{filters.customer_name}%" if filters.customer_name else None,
            "min_value": float(filters.min_value) if filters.min_value is not None else None,
            "max_value": float(filters.max_value) if filters.max_value is not None else None,
            "limit": pagination.page_size,
            "offset": pagination.offset,
        }

        rows = (await self._session.execute(_LIST_ORDERS_SQL, params)).mappings().all()

        if not rows:
            return PaginatedResult(items=[], total=0, page=pagination.page, page_size=pagination.page_size)

        total = int(rows[0]["total_count"])
        orders = [
            Order(
                order_id=row["order_id"],
                customer_id=row["customer_id"],
                customer_name=row["customer_name"],
                status=OrderStatus(row["status"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                total_amount=Decimal(str(row["total_amount"])),
            )
            for row in rows
        ]

        return PaginatedResult(items=orders, total=total, page=pagination.page, page_size=pagination.page_size)

    async def get_by_id(self, order_id: str) -> OrderDetail | None:
        order_row = (await self._session.execute(text("""
            SELECT
                o.order_id, o.status, o.created_at, o.updated_at,
                c.customer_id, c.customer_name, c.customer_email, c.city, c.state
            FROM orders o
            JOIN customers c ON c.customer_id = o.customer_id
            WHERE o.order_id = :order_id
        """), {"order_id": order_id})).mappings().first()

        if not order_row:
            return None

        return await self._fetch_detail(order_row)

    async def create_order(self, payload: OrderWritePayload) -> OrderDetail:
        # Upsert customer
        await self._session.execute(text("""
            INSERT INTO customers (customer_id, customer_name, customer_email, city, state)
            VALUES (:customer_id, :customer_name, :customer_email, :city, :state)
            ON CONFLICT (customer_id) DO UPDATE SET
                customer_name  = EXCLUDED.customer_name,
                customer_email = EXCLUDED.customer_email,
                city           = EXCLUDED.city,
                state          = EXCLUDED.state,
                updated_at     = NOW()
        """), {
            "customer_id": payload.customer_id,
            "customer_name": payload.customer_name,
            "customer_email": payload.customer_email,
            "city": payload.city,
            "state": payload.state,
        })

        # Upsert products
        for item in payload.items:
            await self._session.execute(text("""
                INSERT INTO products (product_id, product_name, category)
                VALUES (:product_id, :product_name, :category)
                ON CONFLICT (product_id) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category     = EXCLUDED.category,
                    updated_at   = NOW()
            """), {"product_id": item.product_id, "product_name": item.product_name, "category": item.category})

        # Generate order_id
        max_row = (await self._session.execute(text(
            "SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1"
        ))).scalar()
        if max_row and max_row.startswith("ORD-"):
            next_num = int(max_row[4:]) + 1
        else:
            next_num = 1
        order_id = f"ORD-{next_num:05d}"

        await self._session.execute(text("""
            INSERT INTO orders (order_id, customer_id, status, created_at, updated_at)
            VALUES (:order_id, :customer_id, :status, :created_at, :updated_at)
        """), {
            "order_id": order_id,
            "customer_id": payload.customer_id,
            "status": payload.status.value,
            "created_at": payload.created_at,
            "updated_at": payload.updated_at,
        })

        for item in payload.items:
            await self._session.execute(text("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct)
                VALUES (:order_id, :product_id, :quantity, :unit_price, :discount_pct)
            """), {
                "order_id": order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "discount_pct": float(item.discount_pct),
            })

        await self._session.flush()

        result = await self.get_by_id(order_id)
        if result is None:
            raise RuntimeError(f"Pedido '{order_id}' não encontrado após inserção.")
        return result

    async def update_order(self, order_id: str, payload: OrderWritePayload) -> OrderDetail | None:
        exists = (await self._session.execute(
            text("SELECT 1 FROM orders WHERE order_id = :id"), {"id": order_id}
        )).scalar()
        if not exists:
            return None

        # Upsert customer
        await self._session.execute(text("""
            INSERT INTO customers (customer_id, customer_name, customer_email, city, state)
            VALUES (:customer_id, :customer_name, :customer_email, :city, :state)
            ON CONFLICT (customer_id) DO UPDATE SET
                customer_name  = EXCLUDED.customer_name,
                customer_email = EXCLUDED.customer_email,
                city           = EXCLUDED.city,
                state          = EXCLUDED.state,
                updated_at     = NOW()
        """), {
            "customer_id": payload.customer_id,
            "customer_name": payload.customer_name,
            "customer_email": payload.customer_email,
            "city": payload.city,
            "state": payload.state,
        })

        await self._session.execute(text("""
            UPDATE orders
            SET customer_id = :customer_id, status = :status,
                created_at = :created_at, updated_at = :updated_at
            WHERE order_id = :order_id
        """), {
            "order_id": order_id,
            "customer_id": payload.customer_id,
            "status": payload.status.value,
            "created_at": payload.created_at,
            "updated_at": payload.updated_at,
        })

        # Replace items
        await self._session.execute(
            text("DELETE FROM order_items WHERE order_id = :order_id"),
            {"order_id": order_id},
        )

        for item in payload.items:
            await self._session.execute(text("""
                INSERT INTO products (product_id, product_name, category)
                VALUES (:product_id, :product_name, :category)
                ON CONFLICT (product_id) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category     = EXCLUDED.category,
                    updated_at   = NOW()
            """), {"product_id": item.product_id, "product_name": item.product_name, "category": item.category})

            await self._session.execute(text("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct)
                VALUES (:order_id, :product_id, :quantity, :unit_price, :discount_pct)
            """), {
                "order_id": order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "discount_pct": float(item.discount_pct),
            })

        await self._session.flush()
        return await self.get_by_id(order_id)

    async def _fetch_detail(self, order_row: RowMapping) -> OrderDetail:
        item_rows = (await self._session.execute(text("""
            SELECT
                oi.id, oi.order_id, oi.product_id,
                p.product_name, p.category,
                oi.quantity, oi.unit_price, oi.discount_pct, oi.total_price
            FROM order_items oi
            JOIN products p ON p.product_id = oi.product_id
            WHERE oi.order_id = :order_id
        """), {"order_id": order_row["order_id"]})).mappings().all()

        items = [
            OrderItem(
                id=str(row["id"]),
                order_id=row["order_id"],
                product_id=row["product_id"],
                product_name=row["product_name"],
                category=row["category"],
                quantity=row["quantity"],
                unit_price=Decimal(str(row["unit_price"])),
                discount_pct=Decimal(str(row["discount_pct"])),
                total_price=Decimal(str(row["total_price"])),
            )
            for row in item_rows
        ]

        total_amount = sum((item.total_price for item in items), Decimal("0"))

        return OrderDetail(
            order_id=order_row["order_id"],
            customer=Customer(
                customer_id=order_row["customer_id"],
                customer_name=order_row["customer_name"],
                customer_email=order_row["customer_email"],
                city=order_row["city"],
                state=order_row["state"],
            ),
            status=OrderStatus(order_row["status"]),
            created_at=order_row["created_at"],
            updated_at=order_row["updated_at"],
            items=items,
            total_amount=total_amount,
        )
