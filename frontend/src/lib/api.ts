import type { Metrics, OrderDetail, OrderFilters, PaginatedOrders } from "@/types";

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
