"use client";

import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { OrderFilters, OrderStatus } from "@/types";

const STATUS_OPTIONS: { value: OrderStatus; label: string }[] = [
  { value: "processing", label: "Em processamento" },
  { value: "shipped", label: "Enviado" },
  { value: "delivered", label: "Entregue" },
  { value: "cancelled", label: "Cancelado" },
];

interface OrdersFiltersProps {
  filters: OrderFilters;
  onChange: (filters: OrderFilters) => void;
  onClear: () => void;
}

export function OrdersFilters({ filters, onChange, onClear }: OrdersFiltersProps) {
  const hasActiveFilters = Object.values(filters).some(
    (v) => v !== undefined && v !== "" && v !== 1 && v !== 20
  );

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar cliente..."
            value={filters.customer_name ?? ""}
            onChange={(e) => onChange({ ...filters, customer_name: e.target.value || undefined, page: 1 })}
            className="pl-8"
          />
        </div>

        <Select
          value={filters.status ?? ""}
          onValueChange={(v) =>
            onChange({ ...filters, status: (v as OrderStatus) || undefined, page: 1 })
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Input
          type="date"
          placeholder="De"
          value={filters.date_from ?? ""}
          onChange={(e) => onChange({ ...filters, date_from: e.target.value || undefined, page: 1 })}
          className="w-[160px]"
        />

        <Input
          type="date"
          placeholder="Até"
          value={filters.date_to ?? ""}
          onChange={(e) => onChange({ ...filters, date_to: e.target.value || undefined, page: 1 })}
          className="w-[160px]"
        />

        <Input
          type="number"
          placeholder="Valor mín."
          value={filters.min_value ?? ""}
          onChange={(e) => onChange({ ...filters, min_value: e.target.value || undefined, page: 1 })}
          className="w-[120px]"
          min={0}
        />

        <Input
          type="number"
          placeholder="Valor máx."
          value={filters.max_value ?? ""}
          onChange={(e) => onChange({ ...filters, max_value: e.target.value || undefined, page: 1 })}
          className="w-[120px]"
          min={0}
        />

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onClear} className="gap-1">
            <X className="h-4 w-4" />
            Limpar
          </Button>
        )}
      </div>
    </div>
  );
}
