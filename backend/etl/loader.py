from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from etl.transformer import ExtractedEntities


@dataclass
class LoadReport:
    customers_upserted: int = 0
    products_upserted: int = 0
    orders_upserted: int = 0
    order_items_inserted: int = 0


def load(session: Session, entities: ExtractedEntities) -> LoadReport:
    report = LoadReport()

    if entities.customers:
        session.execute(
            text("""
                INSERT INTO customers (customer_id, customer_name, customer_email, city, state)
                VALUES (:customer_id, :customer_name, :customer_email, :city, :state)
                ON CONFLICT (customer_id) DO UPDATE SET
                    customer_name  = EXCLUDED.customer_name,
                    customer_email = EXCLUDED.customer_email,
                    city           = EXCLUDED.city,
                    state          = EXCLUDED.state,
                    updated_at     = NOW()
            """),
            list(entities.customers.values()),
        )
        report.customers_upserted = len(entities.customers)

    if entities.products:
        session.execute(
            text("""
                INSERT INTO products (product_id, product_name, category)
                VALUES (:product_id, :product_name, :category)
                ON CONFLICT (product_id) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    category     = EXCLUDED.category,
                    updated_at   = NOW()
            """),
            list(entities.products.values()),
        )
        report.products_upserted = len(entities.products)

    if entities.orders:
        session.execute(
            text("""
                INSERT INTO orders (order_id, customer_id, status, created_at, updated_at)
                VALUES (:order_id, :customer_id, :status, :created_at, :updated_at)
                ON CONFLICT (order_id) DO UPDATE SET
                    status     = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
            """),
            list(entities.orders.values()),
        )
        report.orders_upserted = len(entities.orders)

    for item in entities.order_items:
        result = session.execute(
            text("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct)
                SELECT :order_id, :product_id, :quantity, :unit_price, :discount_pct
                WHERE NOT EXISTS (
                    SELECT 1 FROM order_items
                    WHERE order_id   = :order_id
                      AND product_id = :product_id
                )
            """),
            item,
        )
        report.order_items_inserted += result.rowcount

    session.flush()
    return report
