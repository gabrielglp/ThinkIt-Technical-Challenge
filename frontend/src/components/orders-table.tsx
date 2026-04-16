import Link from "next/link";
import { Eye } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/status-badge";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { Order } from "@/types";

const ROW_HEIGHT = "h-[53px]";

interface OrdersTableProps {
  orders: Order[];
  pageSize?: number;
}

export function OrdersTable({ orders, pageSize }: OrdersTableProps) {
  const emptyRows = pageSize ? Math.max(0, pageSize - orders.length) : 0;

  if (orders.length === 0 && !pageSize) {
    return (
      <div className="flex items-center justify-center py-12 text-muted-foreground text-sm">
        Nenhum pedido encontrado.
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Pedido</TableHead>
          <TableHead>Cliente</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Data</TableHead>
          <TableHead className="text-right">Total</TableHead>
          <TableHead className="w-[60px]" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {orders.length === 0 && pageSize ? (
          <TableRow className={ROW_HEIGHT}>
            <TableCell colSpan={6} className="text-center text-muted-foreground text-sm">
              Nenhum pedido encontrado.
            </TableCell>
          </TableRow>
        ) : (
          <>
            {orders.map((order) => (
              <TableRow key={order.order_id} className={ROW_HEIGHT}>
                <TableCell>
                  <Link
                    href={`/orders/${order.order_id}`}
                    className="font-mono text-sm font-medium text-primary hover:underline"
                  >
                    {order.order_id}
                  </Link>
                </TableCell>
                <TableCell>{order.customer_name}</TableCell>
                <TableCell>
                  <StatusBadge status={order.status} />
                </TableCell>
                <TableCell className="text-muted-foreground">{formatDate(order.created_at)}</TableCell>
                <TableCell className="text-right font-medium">
                  {formatCurrency(order.total_amount)}
                </TableCell>
                <TableCell>
                  <Link href={`/orders/${order.order_id}`}>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
            {Array.from({ length: emptyRows }).map((_, i) => (
              <TableRow key={`empty-${i}`} className={ROW_HEIGHT}>
                <TableCell colSpan={6} />
              </TableRow>
            ))}
          </>
        )}
      </TableBody>
    </Table>
  );
}
