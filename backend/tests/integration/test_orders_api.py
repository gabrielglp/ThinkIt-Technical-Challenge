import uuid

from fastapi.testclient import TestClient


def _auth_header(client: TestClient) -> dict[str, str]:
    email = f"orders_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/auth/register", json={"name": "Orders User", "email": email, "password": "senha123"})
    token = client.post("/auth/login", json={"email": email, "password": "senha123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


_ORDER_PAYLOAD = {
    "customer_id": "CLI-00001",
    "customer_name": "Test Customer",
    "customer_email": "customer@example.com",
    "city": "São Paulo",
    "state": "SP",
    "status": "processing",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00",
    "items": [
        {
            "product_id": "PROD-00001",
            "product_name": "Produto Teste",
            "category": "Eletrônicos",
            "quantity": 2,
            "unit_price": "150.00",
            "discount_pct": "0",
        }
    ],
}


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


class TestCreateOrder:
    def test_returns_201(self, client: TestClient):
        headers = _auth_header(client)
        response = client.post("/orders", json=_ORDER_PAYLOAD, headers=headers)
        assert response.status_code == 201

    def test_response_shape(self, client: TestClient):
        headers = _auth_header(client)
        data = client.post("/orders", json=_ORDER_PAYLOAD, headers=headers).json()
        assert "order_id" in data
        assert "customer" in data
        assert "status" in data
        assert "items" in data
        assert "total_amount" in data

    def test_requires_auth(self, client: TestClient):
        response = client.post("/orders", json=_ORDER_PAYLOAD)
        assert response.status_code in (401, 403)

    def test_missing_items_returns_422(self, client: TestClient):
        headers = _auth_header(client)
        payload = {**_ORDER_PAYLOAD, "items": []}
        response = client.post("/orders", json=payload, headers=headers)
        assert response.status_code == 422

    def test_invalid_customer_id_returns_422(self, client: TestClient):
        headers = _auth_header(client)
        payload = {**_ORDER_PAYLOAD, "customer_id": "INVALID"}
        response = client.post("/orders", json=payload, headers=headers)
        assert response.status_code == 422

    def test_invalid_email_returns_422(self, client: TestClient):
        headers = _auth_header(client)
        payload = {**_ORDER_PAYLOAD, "customer_email": "not-an-email"}
        response = client.post("/orders", json=payload, headers=headers)
        assert response.status_code == 422


class TestUpdateOrder:
    def _create_order(self, client: TestClient, headers: dict[str, str]) -> str:
        return client.post("/orders", json=_ORDER_PAYLOAD, headers=headers).json()["order_id"]

    def test_returns_200(self, client: TestClient):
        headers = _auth_header(client)
        order_id = self._create_order(client, headers)
        updated = {**_ORDER_PAYLOAD, "status": "shipped"}
        response = client.put(f"/orders/{order_id}", json=updated, headers=headers)
        assert response.status_code == 200

    def test_status_is_updated(self, client: TestClient):
        headers = _auth_header(client)
        order_id = self._create_order(client, headers)
        updated = {**_ORDER_PAYLOAD, "status": "delivered"}
        data = client.put(f"/orders/{order_id}", json=updated, headers=headers).json()
        assert data["status"] == "delivered"

    def test_requires_auth(self, client: TestClient):
        headers = _auth_header(client)
        order_id = self._create_order(client, headers)
        response = client.put(f"/orders/{order_id}", json=_ORDER_PAYLOAD)
        assert response.status_code in (401, 403)

    def test_nonexistent_order_returns_404(self, client: TestClient):
        headers = _auth_header(client)
        response = client.put("/orders/ORD-99999", json=_ORDER_PAYLOAD, headers=headers)
        assert response.status_code == 404

    def test_invalid_id_format_returns_422(self, client: TestClient):
        headers = _auth_header(client)
        response = client.put("/orders/INVALID", json=_ORDER_PAYLOAD, headers=headers)
        assert response.status_code == 422
