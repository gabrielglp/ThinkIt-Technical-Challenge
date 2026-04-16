"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Mail, MapPin, Pencil, User } from "lucide-react";
import { fetchOrderById } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { OrderDetailSkeleton } from "@/components/skeletons";
import { formatCurrency, formatDate } from "@/lib/utils";

interface OrderDetailClientProps {
  orderId: string;
}

export function OrderDetailClient({ orderId }: OrderDetailClientProps) {
  const { isAuthenticated } = useAuth();
  const { data: order, isLoading, isError } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => fetchOrderById(orderId),
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <OrderDetailSkeleton />
      </div>
    );
  }

  if (isError || !order) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-4">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Voltar
          </Button>
        </Link>
        <div className="flex items-center justify-center py-24 text-muted-foreground">
          Pedido não encontrado.
        </div>
      </div>
    );
  }

  const { customer, items } = order;

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Voltar
          </Button>
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold font-mono">{order.order_id}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Criado em {formatDate(order.created_at)}
            {" · "}
            Atualizado em {formatDate(order.updated_at)}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={order.status} />
          {isAuthenticated && (
            <Link href={`/dashboard/${order.order_id}/edit`}>
              <Button variant="outline" size="sm" className="gap-2">
                <Pencil className="h-4 w-4" />
                Editar
              </Button>
            </Link>
          )}
        </div>
      </div>

      <Separator />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Cliente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2 text-sm">
              <User className="h-4 w-4 text-muted-foreground shrink-0" />
              <span className="font-medium">{customer.customer_name}</span>
              <span className="text-muted-foreground font-mono text-xs">({customer.customer_id})</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
              <span>{customer.customer_email}</span>
            </div>
            {(customer.city || customer.state) && (
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground shrink-0" />
                <span>
                  {[customer.city, customer.state].filter(Boolean).join(", ")}
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Resumo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Itens</span>
              <span>{items.length}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Unidades</span>
              <span>{items.reduce((acc, i) => acc + i.quantity, 0)}</span>
            </div>
            <Separator />
            <div className="flex justify-between font-semibold">
              <span>Total</span>
              <span>{formatCurrency(order.total_amount)}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Itens do Pedido</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Produto</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead className="text-right">Qtd.</TableHead>
                <TableHead className="text-right">Preço Unit.</TableHead>
                <TableHead className="text-right">Desconto</TableHead>
                <TableHead className="text-right">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div className="font-medium">{item.product_name}</div>
                    <div className="text-xs text-muted-foreground font-mono">{item.product_id}</div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{item.category}</TableCell>
                  <TableCell className="text-right">{item.quantity}</TableCell>
                  <TableCell className="text-right">{formatCurrency(item.unit_price)}</TableCell>
                  <TableCell className="text-right">
                    {item.discount_pct > 0 ? (
                      <span className="text-green-600">-{item.discount_pct}%</span>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {formatCurrency(item.total_price)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
