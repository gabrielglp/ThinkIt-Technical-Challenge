"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { useState } from "react";
import { AuthProvider } from "@/hooks/use-auth";
import { ToastContextProvider } from "@/hooks/use-toast";
import { ToastProvider, ToastViewport } from "@/components/ui/toast";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30 * 1000,
            retry: 1,
          },
        },
      })
  );

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryClientProvider client={queryClient}>
        <NuqsAdapter>
          <AuthProvider>
            <ToastProvider>
              <ToastContextProvider>
                {children}
              </ToastContextProvider>
              <ToastViewport />
            </ToastProvider>
          </AuthProvider>
        </NuqsAdapter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
