import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("E-mail inválido."),
  password: z.string().min(1, "Senha obrigatória."),
});

export const registerSchema = z.object({
  name: z.string().min(2, "Nome deve ter ao menos 2 caracteres."),
  email: z.string().email("E-mail inválido."),
  password: z
    .string()
    .min(8, "Senha deve ter ao menos 8 caracteres.")
    .regex(/\d/, "Senha deve conter ao menos um número."),
});

export const forgotPasswordSchema = z.object({
  email: z.string().email("E-mail inválido."),
});

export const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, "Senha deve ter ao menos 8 caracteres.")
      .regex(/\d/, "Senha deve conter ao menos um número."),
    confirmPassword: z.string().min(1, "Confirmação obrigatória."),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "As senhas não coincidem.",
    path: ["confirmPassword"],
  });

const orderItemSchema = z.object({
  product_id: z.string().regex(/^PROD-\d+$/, "Formato inválido. Use PROD-NNNNN."),
  product_name: z.string().min(1, "Nome do produto obrigatório."),
  category: z.string().min(1, "Categoria obrigatória."),
  quantity: z
    .string()
    .refine((v) => Number.isInteger(Number(v)) && Number(v) >= 1, "Mínimo 1."),
  unit_price: z.number().min(1, "Preço deve ser maior que zero."),
  discount_pct: z
    .string()
    .refine(
      (v) => !isNaN(Number(v)) && Number(v) >= 0 && Number(v) <= 100,
      "Desconto entre 0 e 100."
    ),
});

export const orderSchema = z.object({
  customer_id: z.string().regex(/^CLI-\d+$/, "Formato inválido. Use CLI-NNNNN."),
  customer_name: z.string().min(2, "Nome deve ter ao menos 2 caracteres."),
  customer_email: z.string().email("E-mail inválido."),
  status: z.enum(["processing", "shipped", "delivered", "cancelled"]),
  items: z.array(orderItemSchema).min(1, "Ao menos um item."),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;
export type OrderInput = z.infer<typeof orderSchema>;
