import { MetricCardSkeleton, OrdersTableSkeleton, StatusChartSkeleton } from "@/components/skeletons";

export default function Loading() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCardSkeleton />
        <MetricCardSkeleton />
        <MetricCardSkeleton />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StatusChartSkeleton />
        <StatusChartSkeleton />
      </div>
      <OrdersTableSkeleton />
    </div>
  );
}
