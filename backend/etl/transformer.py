from dataclasses import dataclass

from etl.validators import ValidatedRow


@dataclass
class ExtractedEntities:
    customers: dict[str, dict]
    products: dict[str, dict]
    orders: dict[str, dict]
    order_items: list[dict]


def transform(rows: list[ValidatedRow]) -> ExtractedEntities:
    customers: dict[str, dict] = {}
    products: dict[str, dict] = {}
    orders: dict[str, dict] = {}
    order_items: list[dict] = []

    for row in rows:
        customers[row.customer_id] = {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "customer_email": row.customer_email,
            "city": row.city,
            "state": row.state,
        }

        products[row.product_id] = {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "category": row.category,
        }

        orders[row.order_id] = {
            "order_id": row.order_id,
            "customer_id": row.customer_id,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

        order_items.append({
            "order_id": row.order_id,
            "product_id": row.product_id,
            "quantity": row.quantity,
            "unit_price": float(row.unit_price),
            "discount_pct": float(row.discount_pct),
        })

    return ExtractedEntities(
        customers=customers,
        products=products,
        orders=orders,
        order_items=order_items,
    )
