"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { Moon, Sun, LogIn, UserPlus, LogOut, User } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const { theme, setTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  function handleLogout() {
    logout();
    toast({ title: "Sessão encerrada.", description: "Você saiu da sua conta." });
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-semibold text-foreground">
          <span className="text-primary">⬡</span>
          <span>Função extra</span>
        </Link>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            aria-label="Alternar tema"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>

          {isAuthenticated ? (
            <>
              <Button variant="ghost" size="sm" className="gap-2 hidden sm:flex">
                <User className="h-4 w-4" />
                <span className="max-w-[120px] truncate">{user?.name}</span>
              </Button>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-2 text-destructive hover:text-destructive">
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Sair</span>
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/login" className="gap-2">
                  <LogIn className="h-4 w-4" />
                  <span>Entrar</span>
                </Link>
              </Button>
              <Button size="sm" asChild>
                <Link href="/register" className="gap-2">
                  <UserPlus className="h-4 w-4" />
                  <span>Registrar</span>
                </Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
