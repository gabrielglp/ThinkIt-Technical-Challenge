"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, Search } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { createOrder, updateOrder } from "@/lib/api";
import { orderSchema } from "@/lib/schemas";
import type { OrderDetail, OrderItemWritePayload, OrderStatus, OrderWritePayload } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DatePicker } from "@/components/date-picker";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

function formatCurrency(cents: number): string {
  return (cents / 100).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function parseCurrencyInput(raw: string): number {
  const digits = raw.replace(/\D/g, "");
  return parseInt(digits || "0", 10);
}

function CurrencyInput({
  value,
  onChange,
  id,
  placeholder = "0,00",
}: {
  value: number;
  onChange: (cents: number) => void;
  id?: string;
  placeholder?: string;
}) {
  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const cents = parseCurrencyInput(e.target.value);
    onChange(cents);
  }

  return (
    <Input
      id={id}
      inputMode="numeric"
      placeholder={placeholder}
      value={value === 0 ? "" : formatCurrency(value)}
      onChange={handleChange}
    />
  );
}

const CATEGORIES = [
  "Eletrônicos",
  "Moda",
  "Esportes",
  "Livros",
  "Brinquedos",
  "Casa e Cozinha",
  "Saúde e Beleza",
  "Automotivo",
  "Ferramentas",
  "Alimentos",
  "Outros",
];

function CategoryCombobox({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  const filtered = CATEGORIES.filter((c) =>
    c.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="relative">
      <div className="flex items-center gap-2 rounded-md border border-input bg-background px-3 focus-within:ring-1 focus-within:ring-ring">
        <Search className="h-4 w-4 text-muted-foreground shrink-0" />
        <input
          className="flex h-9 w-full bg-transparent py-1 text-sm outline-none placeholder:text-muted-foreground"
          placeholder="Pesquisar categoria..."
          value={open ? query : value}
          onFocus={() => { setOpen(true); setQuery(""); }}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {open && (
        <ul className="absolute z-50 mt-1 max-h-48 w-full overflow-auto rounded-md border bg-popover p-1 shadow-md">
          {filtered.length === 0 ? (
            <li className="px-2 py-1.5 text-sm text-muted-foreground">Nenhuma categoria encontrada</li>
          ) : (
            filtered.map((cat) => (
              <li
                key={cat}
                className="cursor-pointer rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground"
                onMouseDown={() => { onChange(cat); setOpen(false); }}
              >
                {cat}
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}

interface ItemForm {
  product_id: string;
  product_name: string;
  category: string;
  quantity: string;
  unit_price: number; // cents
  discount_pct: string;
}

function emptyItem(): ItemForm {
  return { product_id: "", product_name: "", category: "", quantity: "1", unit_price: 0, discount_pct: "0" };
}

interface FormState {
  customer_id: string;
  customer_name: string;
  customer_email: string;
  cep: string;
  city: string;
  state: string;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  items: ItemForm[];
}

function fromDetail(order: OrderDetail): FormState {
  return {
    customer_id: order.customer.customer_id,
    customer_name: order.customer.customer_name,
    customer_email: order.customer.customer_email,
    cep: "",
    city: order.customer.city ?? "",
    state: order.customer.state ?? "",
    status: order.status,
    created_at: order.created_at.slice(0, 16),
    updated_at: order.updated_at.slice(0, 16),
    items: order.items.map((i) => ({
      product_id: i.product_id,
      product_name: i.product_name,
      category: i.category,
      quantity: String(i.quantity),
      unit_price: Math.round(i.unit_price * 100),
      discount_pct: String(i.discount_pct),
    })),
  };
}

function toPayload(form: FormState): OrderWritePayload {
  return {
    customer_id: form.customer_id,
    customer_name: form.customer_name,
    customer_email: form.customer_email,
    city: form.city,
    state: form.state,
    status: form.status,
    created_at: form.created_at ? new Date(form.created_at).toISOString() : new Date().toISOString(),
    updated_at: form.updated_at ? new Date(form.updated_at).toISOString() : new Date().toISOString(),
    items: form.items.map((i): OrderItemWritePayload => ({
      product_id: i.product_id,
      product_name: i.product_name,
      category: i.category,
      quantity: parseInt(i.quantity || "1", 10),
      unit_price: i.unit_price / 100,
      discount_pct: parseFloat(i.discount_pct || "0"),
    })),
  };
}

interface Props {
  order?: OrderDetail;
}

export function OrderForm({ order }: Props) {
  const { token } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const now = new Date().toISOString().slice(0, 16);
  const [form, setForm] = useState<FormState>(
    order
      ? fromDetail(order)
      : {
          customer_id: "",
          customer_name: "",
          customer_email: "",
          cep: "",
          city: "",
          state: "",
          status: "processing",
          created_at: now,
          updated_at: now,
          items: [emptyItem()],
        }
  );

  const [cepLoading, setCepLoading] = useState(false);
  const [cepError, setCepError] = useState("");
  const [loading, setLoading] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function lookupCep() {
    const cleaned = form.cep.replace(/\D/g, "");
    if (cleaned.length !== 8) {
      setCepError("CEP deve ter 8 dígitos.");
      return;
    }
    setCepLoading(true);
    setCepError("");
    try {
      const res = await fetch(`https://viacep.com.br/ws/${cleaned}/json/`);
      if (!res.ok) throw new Error();
      const data = (await res.json()) as { erro?: boolean; localidade?: string; uf?: string };
      if (data.erro) throw new Error("CEP não encontrado.");
      setForm((prev) => ({
        ...prev,
        city: data.localidade ?? prev.city,
        state: data.uf ?? prev.state,
      }));
    } catch {
      setCepError("CEP não encontrado.");
    } finally {
      setCepLoading(false);
    }
  }

  function addItem() {
    setForm((prev) => ({ ...prev, items: [...prev.items, emptyItem()] }));
  }

  function removeItem(index: number) {
    setForm((prev) => ({ ...prev, items: prev.items.filter((_, i) => i !== index) }));
  }

  function setItem(index: number, patch: Partial<ItemForm>) {
    setForm((prev) => ({
      ...prev,
      items: prev.items.map((item, i) => (i === index ? { ...item, ...patch } : item)),
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setFormErrors({});

    const result = orderSchema.safeParse({
      customer_id: form.customer_id,
      customer_name: form.customer_name,
      customer_email: form.customer_email,
      status: form.status,
      items: form.items,
    });
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      for (const issue of result.error.issues) {
        const path = issue.path.join(".");
        if (!fieldErrors[path]) fieldErrors[path] = issue.message;
      }
      setFormErrors(fieldErrors);
      toast({ title: "Corrija os erros antes de salvar.", variant: "destructive" });
      return;
    }

    setLoading(true);
    try {
      const payload = toPayload(form);
      if (order) {
        await updateOrder(order.order_id, payload, token);
        toast({ title: "Pedido atualizado com sucesso!" });
      } else {
        await createOrder(payload, token);
        toast({ title: "Pedido criado com sucesso!" });
      }
      router.push("/dashboard");
      router.refresh();
    } catch {
      toast({
        title: order ? "Erro ao atualizar pedido." : "Erro ao criar pedido.",
        description: "Verifique os dados e tente novamente.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Customer section */}
      <section className="space-y-4">
        <h2 className="text-base font-semibold">Dados do cliente</h2>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="customer_id">ID do cliente</Label>
            <Input
              id="customer_id"
              value={form.customer_id}
              onChange={(e) => setField("customer_id", e.target.value)}
              placeholder="CLI-00001"
              aria-invalid={!!formErrors.customer_id}
            />
            {formErrors.customer_id && <p className="text-xs text-destructive">{formErrors.customer_id}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="customer_name">Nome do cliente</Label>
            <Input
              id="customer_name"
              value={form.customer_name}
              onChange={(e) => setField("customer_name", e.target.value)}
              placeholder="João Silva"
              aria-invalid={!!formErrors.customer_name}
            />
            {formErrors.customer_name && <p className="text-xs text-destructive">{formErrors.customer_name}</p>}
          </div>
          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="customer_email">E-mail do cliente</Label>
            <Input
              id="customer_email"
              type="email"
              value={form.customer_email}
              onChange={(e) => setField("customer_email", e.target.value)}
              placeholder="cliente@email.com"
              aria-invalid={!!formErrors.customer_email}
            />
            {formErrors.customer_email && <p className="text-xs text-destructive">{formErrors.customer_email}</p>}
          </div>
        </div>

        {/* CEP lookup */}
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="cep">CEP</Label>
            <div className="flex gap-2">
              <Input
                id="cep"
                value={form.cep}
                onChange={(e) => setField("cep", e.target.value)}
                placeholder="00000-000"
                maxLength={9}
              />
              <Button type="button" variant="outline" onClick={lookupCep} disabled={cepLoading}>
                {cepLoading ? "..." : "Buscar"}
              </Button>
            </div>
            {cepError && <p className="text-xs text-destructive">{cepError}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="city">Cidade</Label>
            <Input
              id="city"
              value={form.city}
              onChange={(e) => setField("city", e.target.value)}
              placeholder="São Paulo"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="state">Estado (UF)</Label>
            <Input
              id="state"
              value={form.state}
              onChange={(e) => setField("state", e.target.value)}
              placeholder="SP"
              maxLength={2}
            />
          </div>
        </div>
      </section>

      {/* Order metadata */}
      <section className="space-y-4">
        <h2 className="text-base font-semibold">Dados do pedido</h2>

        <div className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select value={form.status} onValueChange={(v) => setField("status", v as OrderStatus)}>
              <SelectTrigger id="status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="processing">Processando</SelectItem>
                <SelectItem value="shipped">Enviado</SelectItem>
                <SelectItem value="delivered">Entregue</SelectItem>
                <SelectItem value="cancelled">Cancelado</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Criado em</Label>
            <DatePicker
              value={form.created_at?.slice(0, 10)}
              onChange={(d) =>
                setField("created_at", d ? `${d}T${form.created_at?.slice(11, 16) || "00:00"}` : "")
              }
            />
          </div>
          <div className="space-y-2">
            <Label>Atualizado em</Label>
            <DatePicker
              value={form.updated_at?.slice(0, 10)}
              onChange={(d) =>
                setField("updated_at", d ? `${d}T${form.updated_at?.slice(11, 16) || "00:00"}` : "")
              }
            />
          </div>
        </div>
      </section>

      {/* Items */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Itens do pedido</h2>
          <Button type="button" variant="outline" size="sm" onClick={addItem} className="gap-2">
            <Plus className="h-4 w-4" />
            Adicionar item
          </Button>
        </div>

        {form.items.map((item, i) => (
          <div key={i} className="rounded-lg border bg-card p-4 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-muted-foreground">Item {i + 1}</span>
              {form.items.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeItem(i)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>ID do produto</Label>
                <Input
                  value={item.product_id}
                  onChange={(e) => setItem(i, { product_id: e.target.value })}
                  placeholder="PROD-001"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Nome do produto</Label>
                <Input
                  value={item.product_name}
                  onChange={(e) => setItem(i, { product_name: e.target.value })}
                  placeholder="Produto XYZ"
                  required
                />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Categoria</Label>
                <CategoryCombobox
                  value={item.category}
                  onChange={(v) => setItem(i, { category: v })}
                />
              </div>
              <div className="space-y-2">
                <Label>Quantidade</Label>
                <Input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => setItem(i, { quantity: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Preço unitário (R$)</Label>
                <CurrencyInput
                  value={item.unit_price}
                  onChange={(cents) => setItem(i, { unit_price: cents })}
                />
              </div>
              <div className="space-y-2">
                <Label>Desconto (%)</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={item.discount_pct}
                  onChange={(e) => setItem(i, { discount_pct: e.target.value })}
                  placeholder="0"
                />
              </div>
            </div>
          </div>
        ))}
      </section>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={() => router.back()}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? "Salvando..." : order ? "Salvar alterações" : "Criar pedido"}
        </Button>
      </div>
    </form>
  );
}
