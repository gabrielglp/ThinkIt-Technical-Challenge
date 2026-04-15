from fastapi.testclient import TestClient


class TestListOrders:
    def test_returns_200(self, client: TestClient):
        response = client.get("/orders")
        assert response.status_code == 200

    def test_response_shape(self, client: TestClient):
        data = client.get("/orders").json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert "has_next" in data
        assert "has_previous" in data

    def test_item_shape(self, client: TestClient):
        items = client.get("/orders?page_size=1").json()["items"]
        assert len(items) == 1
        item = items[0]
        assert "order_id" in item
        assert "customer_id" in item
        assert "customer_name" in item
        assert "status" in item
        assert "created_at" in item
        assert "total_amount" in item

    def test_pagination_defaults(self, client: TestClient):
        data = client.get("/orders").json()
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["items"]) <= 20

    def test_custom_page_size(self, client: TestClient):
        data = client.get("/orders?page_size=5").json()
        assert len(data["items"]) <= 5

    def test_filter_by_status(self, client: TestClient):
        data = client.get("/orders?status=delivered&page_size=10").json()
        assert client.get("/orders?status=delivered").status_code == 200
        for item in data["items"]:
            assert item["status"] == "delivered"

    def test_invalid_status_returns_422(self, client: TestClient):
        assert client.get("/orders?status=unknown").status_code == 422

    def test_page_size_above_max_returns_422(self, client: TestClient):
        assert client.get("/orders?page_size=101").status_code == 422

    def test_page_below_min_returns_422(self, client: TestClient):
        assert client.get("/orders?page=0").status_code == 422

    def test_has_previous_false_on_first_page(self, client: TestClient):
        assert client.get("/orders?page=1&page_size=10").json()["has_previous"] is False

    def test_second_page_has_previous(self, client: TestClient):
        assert client.get("/orders?page=2&page_size=10").json()["has_previous"] is True

    def test_filter_by_customer_name(self, client: TestClient):
        data = client.get("/orders?customer_name=a&page_size=5").json()
        assert client.get("/orders?customer_name=a").status_code == 200
        for item in data["items"]:
            assert "a" in item["customer_name"].lower()

    def test_filter_min_value(self, client: TestClient):
        data = client.get("/orders?min_value=500&page_size=5").json()
        for item in data["items"]:
            assert item["total_amount"] >= 500


class TestGetOrderById:
    def _first_order_id(self, client: TestClient) -> str:
        return client.get("/orders?page_size=1").json()["items"][0]["order_id"]

    def test_returns_200_for_existing_order(self, client: TestClient):
        order_id = self._first_order_id(client)
        assert client.get(f"/orders/{order_id}").status_code == 200

    def test_response_shape(self, client: TestClient):
        order_id = self._first_order_id(client)
        data = client.get(f"/orders/{order_id}").json()
        assert "order_id" in data
        assert "customer" in data
        assert "status" in data
        assert "items" in data
        assert "total_amount" in data

    def test_customer_shape(self, client: TestClient):
        order_id = self._first_order_id(client)
        customer = client.get(f"/orders/{order_id}").json()["customer"]
        assert "customer_id" in customer
        assert "customer_name" in customer
        assert "customer_email" in customer

    def test_item_shape(self, client: TestClient):
        order_id = self._first_order_id(client)
        items = client.get(f"/orders/{order_id}").json()["items"]
        assert len(items) >= 1
        item = items[0]
        assert "product_id" in item
        assert "product_name" in item
        assert "quantity" in item
        assert "unit_price" in item
        assert "discount_pct" in item
        assert "total_price" in item

    def test_returns_404_for_nonexistent_order(self, client: TestClient):
        assert client.get("/orders/ORD-99999").status_code == 404

    def test_404_response_has_detail(self, client: TestClient):
        data = client.get("/orders/ORD-99999").json()
        assert "detail" in data
