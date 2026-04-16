"use client";

import { useState } from "react";
import Link from "next/link";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { parseAsInteger, parseAsString, useQueryStates } from "nuqs";
import { Clock, DollarSign, Loader2, Package, Plus, TrendingUp, Upload } from "lucide-react";
import { fetchMetrics, fetchOrders } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { MetricCard } from "@/components/metric-card";
import { OrdersFilters } from "@/components/orders-filters";
import { OrdersTable } from "@/components/orders-table";
import { PaginationControls } from "@/components/pagination-controls";
import { StatusChart } from "@/components/status-chart";
import { StatusLineChart } from "@/components/status-line-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { MetricCardSkeleton, OrdersTableSkeleton, StatusChartSkeleton } from "@/components/skeletons";
import { CsvImportDialog } from "@/components/csv-import-dialog";
import { cn, formatCurrency } from "@/lib/utils";
import type { OrderFilters, OrderStatus } from "@/types";

const PAGE_SIZE = 10;

const FILTER_PARSERS = {
  customer_name: parseAsString,
  status: parseAsString,
  date_from: parseAsString,
  date_to: parseAsString,
  min_value: parseAsString,
  max_value: parseAsString,
  page: parseAsInteger.withDefault(1),
};

export function DashboardClient() {
  const { isAuthenticated } = useAuth();
  const [importOpen, setImportOpen] = useState(false);
  const [params, setParams] = useQueryStates(FILTER_PARSERS, {
    shallow: true,
  });

  const filters: OrderFilters = {
    customer_name: params.customer_name ?? undefined,
    status: (params.status as OrderStatus) ?? undefined,
    date_from: params.date_from ? `${params.date_from}T00:00:00` : undefined,
    date_to: params.date_to ? `${params.date_to}T23:59:59` : undefined,
    min_value: params.min_value ?? undefined,
    max_value: params.max_value ?? undefined,
    page: params.page,
    page_size: PAGE_SIZE,
  };

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["metrics"],
    queryFn: fetchMetrics,
  });

  const {
    data: orders,
    isLoading: ordersLoading,
    isFetching: ordersFetching,
  } = useQuery({
    queryKey: ["orders", params],
    queryFn: () => fetchOrders(filters),
    placeholderData: keepPreviousData,
  });

  function handleFilterChange(next: OrderFilters) {
    setParams({
      customer_name: next.customer_name ?? null,
      status: next.status ?? null,
      date_from: next.date_from ? next.date_from.split("T")[0] : null,
      date_to: next.date_to ? next.date_to.split("T")[0] : null,
      min_value: next.min_value ?? null,
      max_value: next.max_value ?? null,
      page: next.page ?? 1,
    });
  }

  function handleClear() {
    setParams({
      customer_name: null,
      status: null,
      date_from: null,
      date_to: null,
      min_value: null,
      max_value: null,
      page: 1,
    });
  }

  const uiFilters: OrderFilters = {
    customer_name: params.customer_name ?? undefined,
    status: (params.status as OrderStatus) ?? undefined,
    date_from: params.date_from ?? undefined,
    date_to: params.date_to ?? undefined,
    min_value: params.min_value ?? undefined,
    max_value: params.max_value ?? undefined,
    page: params.page,
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard de Pedidos</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Visão geral das métricas e listagem de pedidos
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricsLoading ? (
          <>
            <MetricCardSkeleton />
            <MetricCardSkeleton />
            <MetricCardSkeleton />
            <MetricCardSkeleton />
          </>
        ) : metrics ? (
          <>
            <MetricCard
              title="Total de Pedidos"
              value={metrics.total_orders.toLocaleString("pt-BR")}
              icon={Package}
            />
            <MetricCard
              title="Pedidos Pendentes"
              value={(metrics.orders_by_status.find((s) => s.status === "processing")?.count ?? 0).toLocaleString("pt-BR")}
              icon={Clock}
            />
            <MetricCard
              title="Receita Total"
              value={formatCurrency(metrics.total_revenue)}
              icon={DollarSign}
            />
            <MetricCard
              title="Ticket Médio"
              value={formatCurrency(metrics.average_ticket)}
              icon={TrendingUp}
            />
          </>
        ) : null}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Pedidos por Status</CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading ? (
              <StatusChartSkeleton />
            ) : metrics ? (
              <StatusLineChart data={metrics.orders_by_status} />
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top 5 Produtos</CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading ? (
              <OrdersTableSkeleton />
            ) : metrics ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Produto</TableHead>
                    <TableHead>Categoria</TableHead>
                    <TableHead className="text-right">Receita</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {metrics.top_products.map((p) => (
                    <TableRow key={p.product_id}>
                      <TableCell className="font-medium">{p.product_name}</TableCell>
                      <TableCell className="text-muted-foreground">{p.category}</TableCell>
                      <TableCell className="text-right">{formatCurrency(p.total_revenue)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : null}
          </CardContent>
        </Card>
      </div>

      <Separator />

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="text-base">
              Pedidos
              {orders && (
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  ({orders.total.toLocaleString("pt-BR")} resultados)
                </span>
              )}
            </CardTitle>
            <div className="flex items-center gap-2">
              {ordersFetching && !ordersLoading && (
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              )}
              {isAuthenticated && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    onClick={() => setImportOpen(true)}
                  >
                    <Upload className="h-4 w-4" />
                    <span className="hidden sm:inline">Importar CSV</span>
                  </Button>
                  <Button size="sm" asChild className="gap-2">
                    <Link href="/dashboard/new">
                      <Plus className="h-4 w-4" />
                      <span className="hidden sm:inline">Novo pedido</span>
                    </Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </CardHeader>
        <CsvImportDialog open={importOpen} onOpenChange={setImportOpen} />
        <CardContent className="space-y-4">
          <OrdersFilters
            filters={uiFilters}
            onChange={handleFilterChange}
            onClear={handleClear}
          />

          {ordersLoading ? (
            <OrdersTableSkeleton rows={PAGE_SIZE} />
          ) : (
            <div className={cn("transition-opacity duration-200", ordersFetching && "opacity-50")}>
              <OrdersTable orders={orders?.items ?? []} pageSize={PAGE_SIZE} />
              {orders && orders.total_pages > 1 && (
                <div className="mt-4">
                  <PaginationControls
                    page={orders.page}
                    totalPages={orders.total_pages}
                    hasNext={orders.has_next}
                    hasPrevious={orders.has_previous}
                    onPageChange={(p) => setParams({ page: p })}
                  />
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
