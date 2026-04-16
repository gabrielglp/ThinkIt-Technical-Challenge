"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Mail } from "lucide-react";
import { forgotPassword } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type State = "idle" | "loading" | "success" | "error";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [state, setState] = useState<State>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setState("loading");
    setErrorMsg("");
    try {
      await forgotPassword(email);
      setState("success");
    } catch {
      setErrorMsg("Falha ao enviar o e-mail. Tente novamente.");
      setState("error");
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-56px)]">
      {/* Left decorative panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-primary p-12 text-primary-foreground">
        <div className="flex items-center gap-2 text-lg font-semibold">
          <span>⬡</span>
          <span>Função extra</span>
        </div>
        <div className="space-y-4">
          <blockquote className="text-2xl font-light leading-relaxed">
            "Não se preocupe — um link seguro será enviado para você redefinir seu acesso."
          </blockquote>
          <p className="text-sm opacity-70">Recuperação de acesso segura</p>
        </div>
        <p className="text-xs opacity-50">© 2024 Função extra</p>
      </div>

      {/* Right form panel */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8">
        <div className="w-full max-w-sm space-y-8">
          <div className="space-y-2 text-center">
            <div className="flex justify-center">
              <div className="rounded-full bg-muted p-3">
                <Mail className="h-6 w-6 text-muted-foreground" />
              </div>
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Esqueceu a senha?</h1>
            <p className="text-sm text-muted-foreground">
              Informe seu e-mail e enviaremos um link para redefinir sua senha.
            </p>
          </div>

          {state === "success" ? (
            <div className="space-y-6">
              <div className="rounded-lg border border-green-500/30 bg-green-500/10 p-5 text-center">
                <p className="font-medium text-green-600 dark:text-green-400">
                  E-mail enviado!
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Se <strong>{email}</strong> estiver cadastrado, você receberá um link de redefinição em instantes.
                </p>
              </div>
              <Button asChild className="w-full">
                <Link href="/login">Voltar para o login</Link>
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              {state === "error" && (
                <p className="text-sm text-destructive">{errorMsg}</p>
              )}

              <Button type="submit" className="w-full" disabled={state === "loading"}>
                {state === "loading" ? "Enviando..." : "Enviar link de redefinição"}
              </Button>
            </form>
          )}

          <div className="text-center">
            <Link
              href="/login"
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-3 w-3" />
              Voltar para o login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
