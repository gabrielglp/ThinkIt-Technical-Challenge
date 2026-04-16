import type { AuthToken, ImportCsvReport, Metrics, OrderDetail, OrderFilters, OrderWritePayload, PaginatedOrders } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== "" && value !== null) {
        url.searchParams.set(key, value);
      }
    });
  }

  const response = await fetch(url.toString(), { next: { revalidate: 0 } });

  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${await response.text()}`);
  }

  return response.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json() as Promise<T>;
}

async function put<T>(path: string, body: unknown, token: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json() as Promise<T>;
}

export function fetchOrders(filters: OrderFilters = {}): Promise<PaginatedOrders> {
  const params: Record<string, string> = {};

  if (filters.status) params.status = filters.status;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  if (filters.min_value) params.min_value = filters.min_value;
  if (filters.max_value) params.max_value = filters.max_value;
  if (filters.customer_name) params.customer_name = filters.customer_name;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);

  return get<PaginatedOrders>("/orders", params);
}

export function fetchOrderById(orderId: string): Promise<OrderDetail> {
  return get<OrderDetail>(`/orders/${encodeURIComponent(orderId)}`);
}

export function fetchMetrics(): Promise<Metrics> {
  return get<Metrics>("/metrics");
}

export function registerUser(name: string, email: string, password: string): Promise<AuthToken> {
  return post<AuthToken>("/auth/register", { name, email, password });
}

export async function forgotPassword(email: string): Promise<void> {
  await post<{ message: string }>("/auth/forgot-password", { email });
}

export async function resetPassword(token: string, password: string, confirmPassword: string): Promise<void> {
  await post<{ message: string }>(`/auth/reset-password/${encodeURIComponent(token)}`, {
    password,
    confirm_password: confirmPassword,
  });
}

export function loginUser(email: string, password: string): Promise<AuthToken> {
  return post<AuthToken>("/auth/login", { email, password });
}

export function createOrder(payload: OrderWritePayload, token: string): Promise<OrderDetail> {
  return post<OrderDetail>("/orders", payload, token);
}

export function updateOrder(orderId: string, payload: OrderWritePayload, token: string): Promise<OrderDetail> {
  return put<OrderDetail>(`/orders/${encodeURIComponent(orderId)}`, payload, token);
}

export async function importCsv(file: File, token: string): Promise<ImportCsvReport> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${BASE_URL}/orders/import`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json() as Promise<ImportCsvReport>;
}

