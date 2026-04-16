"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { fetchOrderById } from "@/lib/api";
import { OrderForm } from "@/components/order-form";

export default function EditOrderPage() {
  const params = useParams();
  const orderId = params.id as string;
  const { isHydrated, isAuthenticated } = useAuth();

  const { data: order, isLoading, isError } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => fetchOrderById(orderId),
    enabled: isHydrated && isAuthenticated,
  });

  if (!isHydrated || !isAuthenticated) return null;

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
      </div>
    );
  }

  if (isError || !order) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <p className="text-destructive">Pedido não encontrado.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Editar pedido</h1>
        <p className="text-sm text-muted-foreground mt-1">{order.order_id}</p>
      </div>
      <OrderForm order={order} />
    </div>
  );
}
