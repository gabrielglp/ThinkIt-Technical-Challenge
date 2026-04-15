from fastapi.testclient import TestClient


class TestGetMetrics:
    def test_returns_200(self, client: TestClient):
        assert client.get("/metrics").status_code == 200

    def test_response_shape(self, client: TestClient):
        data = client.get("/metrics").json()
        assert "average_ticket" in data
        assert "total_revenue" in data
        assert "total_orders" in data
        assert "top_products" in data
        assert "orders_by_status" in data

    def test_total_orders_positive(self, client: TestClient):
        assert client.get("/metrics").json()["total_orders"] > 0

    def test_average_ticket_positive(self, client: TestClient):
        assert client.get("/metrics").json()["average_ticket"] > 0

    def test_total_revenue_positive(self, client: TestClient):
        assert client.get("/metrics").json()["total_revenue"] > 0

    def test_top_products_at_most_five(self, client: TestClient):
        assert len(client.get("/metrics").json()["top_products"]) <= 5

    def test_top_product_shape(self, client: TestClient):
        products = client.get("/metrics").json()["top_products"]
        assert len(products) >= 1
        p = products[0]
        assert "product_id" in p
        assert "product_name" in p
        assert "category" in p
        assert "total_revenue" in p
        assert "total_quantity" in p

    def test_orders_by_status_shape(self, client: TestClient):
        entries = client.get("/metrics").json()["orders_by_status"]
        assert len(entries) >= 1
        assert "status" in entries[0]
        assert "count" in entries[0]

    def test_orders_by_status_valid_values(self, client: TestClient):
        valid_statuses = {"processing", "shipped", "delivered", "cancelled"}
        for entry in client.get("/metrics").json()["orders_by_status"]:
            assert entry["status"] in valid_statuses
            assert entry["count"] > 0

    def test_top_products_ordered_by_revenue_desc(self, client: TestClient):
        revenues = [p["total_revenue"] for p in client.get("/metrics").json()["top_products"]]
        assert revenues == sorted(revenues, reverse=True)
