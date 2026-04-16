"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import type { StatusCount } from "@/types";

const STATUS_COLORS: Record<string, string> = {
  processing: "#3b82f6",
  shipped:    "#f59e0b",
  delivered:  "#22c55e",
  cancelled:  "#ef4444",
};

const STATUS_LABELS: Record<string, string> = {
  processing: "Em processamento",
  shipped:    "Enviado",
  delivered:  "Entregue",
  cancelled:  "Cancelado",
};

interface StatusChartProps {
  data: StatusCount[];
}

export function StatusChart({ data }: StatusChartProps) {
  const total = data.reduce((sum, d) => sum + d.count, 0);

  const chartData = data.map((item) => ({
    name:  STATUS_LABELS[item.status] ?? item.status,
    value: item.count,
    color: STATUS_COLORS[item.status] ?? "#94a3b8",
    pct:   total > 0 ? ((item.count / total) * 100).toFixed(1) : "0",
  }));

  return (
    <div className="flex items-center gap-6">
      {/* Stats list */}
      <div className="flex flex-col gap-3 flex-1 min-w-0">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center gap-2">
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full"
              style={{ background: item.color }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs text-muted-foreground truncate">{item.name}</p>
              <p className="text-sm font-semibold leading-tight">
                {item.value.toLocaleString("pt-BR")}
                <span className="ml-1.5 text-xs font-normal text-muted-foreground">
                  {item.pct}%
                </span>
              </p>
            </div>
          </div>
        ))}
        <p className="text-xs text-muted-foreground pt-1 border-t">
          Total: <span className="font-semibold text-foreground">{total.toLocaleString("pt-BR")}</span>
        </p>
      </div>

      {/* Donut chart */}
      <div className="shrink-0 w-[180px] h-[180px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={52}
              outerRadius={82}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => [value.toLocaleString("pt-BR"), "Pedidos"]}
              contentStyle={{
                fontSize: 12,
                borderRadius: 8,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
