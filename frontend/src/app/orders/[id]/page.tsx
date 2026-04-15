import { OrderDetailClient } from "./_components/order-detail-client";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  return { title: `${id} | Orders Dashboard` };
}

export default async function OrderDetailPage({ params }: Props) {
  const { id } = await params;
  return <OrderDetailClient orderId={id} />;
}
