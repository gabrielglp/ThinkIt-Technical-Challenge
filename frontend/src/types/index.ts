export type OrderStatus = "processing" | "shipped" | "delivered" | "cancelled";

export interface Order {
  order_id: string;
  customer_id: string;
  customer_name: string;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  total_amount: number;
}

export interface Customer {
  customer_id: string;
  customer_name: string;
  customer_email: string;
  city: string | null;
  state: string | null;
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  category: string;
  quantity: number;
  unit_price: number;
  discount_pct: number;
  total_price: number;
}

export interface OrderDetail {
  order_id: string;
  customer: Customer;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
  total_amount: number;
}

export interface PaginatedOrders {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface TopProduct {
  product_id: string;
  product_name: string;
  category: string;
  total_revenue: number;
  total_quantity: number;
}

export interface StatusCount {
  status: OrderStatus;
  count: number;
}

export interface Metrics {
  average_ticket: number;
  total_revenue: number;
  total_orders: number;
  top_products: TopProduct[];
  orders_by_status: StatusCount[];
}

export interface OrderFilters {
  status?: OrderStatus;
  date_from?: string;
  date_to?: string;
  min_value?: string;
  max_value?: string;
  customer_name?: string;
  page?: number;
  page_size?: number;
}
