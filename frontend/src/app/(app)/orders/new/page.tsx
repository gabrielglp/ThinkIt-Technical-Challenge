"use client";

import { useAuth } from "@/hooks/use-auth";
import { OrderForm } from "@/components/order-form";

export default function NewOrderPage() {
  const { isHydrated, isAuthenticated } = useAuth();

  if (!isHydrated || !isAuthenticated) return null;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Novo pedido</h1>
        <p className="text-sm text-muted-foreground mt-1">Preencha os dados do pedido abaixo</p>
      </div>
      <OrderForm />
    </div>
  );
}
