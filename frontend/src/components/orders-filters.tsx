"use client";

import { useState } from "react";
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
import { DateRangePicker } from "@/components/date-range-picker";
import type { OrderFilters, OrderStatus } from "@/types";

const STATUS_OPTIONS: { value: OrderStatus; label: string }[] = [
  { value: "processing", label: "Em processamento" },
  { value: "shipped", label: "Enviado" },
  { value: "delivered", label: "Entregue" },
  { value: "cancelled", label: "Cancelado" },
];

function formatCents(cents: number): string {
  if (cents === 0) return "";
  return (cents / 100).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function parseCents(raw: string): number {
  const digits = raw.replace(/\D/g, "");
  return parseInt(digits || "0", 10);
}

interface CurrencyFilterInputProps {
  placeholder: string;
  value: string | undefined;
  onCommit: (value: string | undefined) => void;
  className?: string;
}

function CurrencyFilterInput({ placeholder, value, onCommit, className }: CurrencyFilterInputProps) {
  const initialCents = value ? Math.round(parseFloat(value) * 100) : 0;
  const [cents, setCents] = useState(initialCents);
  const [display, setDisplay] = useState(formatCents(initialCents));

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const c = parseCents(e.target.value);
    setCents(c);
    setDisplay(formatCents(c));
  }

  function commit() {
    onCommit(cents > 0 ? (cents / 100).toFixed(2) : undefined);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") commit();
  }

  function handleBlur() {
    commit();
  }

  return (
    <Input
      inputMode="numeric"
      placeholder={placeholder}
      value={display}
      onChange={handleChange}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
      className={className}
    />
  );
}

interface OrdersFiltersProps {
  filters: OrderFilters;
  onChange: (filters: OrderFilters) => void;
  onClear: () => void;
}

export function OrdersFilters({ filters, onChange, onClear }: OrdersFiltersProps) {
  const [clearKey, setClearKey] = useState(0);

  const hasActiveFilters = Object.values(filters).some(
    (v) => v !== undefined && v !== "" && v !== 1 && v !== 20
  );

  function handleClear() {
    setClearKey((k) => k + 1);
    onClear();
  }

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

        <DateRangePicker
          startDate={filters.date_from}
          endDate={filters.date_to}
          onChange={(start, end) =>
            onChange({ ...filters, date_from: start, date_to: end, page: 1 })
          }
        />

        <CurrencyFilterInput
          key={`min-${clearKey}`}
          placeholder="Valor mín."
          value={filters.min_value}
          onCommit={(v) => onChange({ ...filters, min_value: v, page: 1 })}
          className="w-[130px]"
        />

        <CurrencyFilterInput
          key={`max-${clearKey}`}
          placeholder="Valor máx."
          value={filters.max_value}
          onCommit={(v) => onChange({ ...filters, max_value: v, page: 1 })}
          className="w-[130px]"
        />

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={handleClear} className="gap-1">
            <X className="h-4 w-4" />
            Limpar
          </Button>
        )}
      </div>
    </div>
  );
}
