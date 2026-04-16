"use client";

import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { cn } from "@/lib/utils";
import type { StatusCount } from "@/types";

const CONFIG = {
  processing: { label: "Em processamento", color: "#3b82f6" },
  shipped:    { label: "Enviado",           color: "#a855f7" },
  delivered:  { label: "Entregue",         color: "#22c55e" },
  cancelled:  { label: "Cancelado",        color: "#f43f5e" },
} as const;

type StatusKey = keyof typeof CONFIG;

interface Props {
  data: StatusCount[];
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; payload: { key: string } }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const key = payload[0].payload.key as StatusKey;
  const cfg = CONFIG[key];
  return (
    <div className="rounded-lg border bg-popover text-popover-foreground shadow-md px-3 py-2 text-xs">
      <span className="flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full" style={{ background: cfg.color }} />
        {cfg.label}
      </span>
      <p className="mt-1 font-semibold">{payload[0].value.toLocaleString("pt-BR")} pedidos</p>
    </div>
  );
}

export function StatusLineChart({ data }: Props) {
  const [hidden, setHidden] = useState<Set<StatusKey>>(new Set());

  function toggle(key: StatusKey) {
    setHidden((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  }

  const chartData = data
    .map((d) => ({
      key:   d.status as StatusKey,
      label: CONFIG[d.status as StatusKey]?.label ?? d.status,
      value: d.count,
      color: CONFIG[d.status as StatusKey]?.color ?? "#94a3b8",
    }))
    .filter((d) => !hidden.has(d.key));

  return (
    <div className="space-y-4">
      {/* Pill legend */}
      <div className="flex flex-wrap gap-2">
        {(Object.keys(CONFIG) as StatusKey[]).map((key) => {
          const off = hidden.has(key);
          return (
            <button
              key={key}
              onClick={() => toggle(key)}
              className={cn(
                "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-opacity",
                off ? "border-border text-muted-foreground opacity-40" : "border-border text-foreground"
              )}
            >
              <span
                className="h-2 w-2 rounded-full"
                style={{ background: off ? "hsl(var(--muted-foreground))" : CONFIG[key].color }}
              />
              {CONFIG[key].label}
            </button>
          );
        })}
      </div>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData} margin={{ top: 4, right: 4, left: -8, bottom: 0 }} barCategoryGap="35%">
          <CartesianGrid stroke="hsl(var(--border))" vertical={false} strokeDasharray="3 3" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
            width={36}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "hsl(var(--muted))" }} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {chartData.map((entry) => (
              <Cell key={entry.key} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
