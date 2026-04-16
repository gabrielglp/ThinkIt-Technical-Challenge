"use client";

import { useRef, useState } from "react";
import { Upload, FileText, CheckCircle, XCircle } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { importCsv } from "@/lib/api";
import type { ImportCsvReport } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type State = "idle" | "loading" | "success" | "error";

export function CsvImportDialog({ open, onOpenChange }: Props) {
  const { token } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<State>("idle");
  const [report, setReport] = useState<ImportCsvReport | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");

  function handleClose(val: boolean) {
    if (!val) {
      setFile(null);
      setState("idle");
      setReport(null);
      setErrorMsg("");
    }
    onOpenChange(val);
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setFile(selected);
    setState("idle");
    setReport(null);
  }

  async function handleImport() {
    if (!file || !token) return;
    setState("loading");
    try {
      const result = await importCsv(file, token);
      setReport(result);
      setState("success");
      await queryClient.invalidateQueries({ queryKey: ["orders"] });
      await queryClient.invalidateQueries({ queryKey: ["metrics"] });
      toast({
        title: "Importação concluída!",
        description: `${result.valid_rows} linha(s) importada(s), ${result.invalid_rows} inválida(s).`,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erro ao importar.";
      setErrorMsg(msg);
      setState("error");
      toast({ title: "Erro ao importar CSV.", description: msg, variant: "destructive" });
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Importar pedidos via CSV</DialogTitle>
          <DialogDescription>
            Selecione um arquivo .csv com os dados dos pedidos.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div
            className="flex cursor-pointer flex-col items-center gap-3 rounded-lg border-2 border-dashed border-border p-8 text-center transition-colors hover:border-primary/60 hover:bg-muted/40"
            onClick={() => inputRef.current?.click()}
          >
            <Upload className="h-8 w-8 text-muted-foreground" />
            {file ? (
              <div className="flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4 text-primary" />
                <span className="font-medium">{file.name}</span>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Clique para selecionar ou arraste um arquivo .csv
              </p>
            )}
            <input
              ref={inputRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {state === "success" && report && (
            <div className="rounded-lg border border-green-500/30 bg-green-500/10 p-4 text-sm space-y-1">
              <div className="flex items-center gap-2 font-medium text-green-600 dark:text-green-400">
                <CheckCircle className="h-4 w-4" />
                Importação concluída
              </div>
              <p>Linhas válidas: {report.valid_rows}</p>
              <p>Linhas inválidas: {report.invalid_rows}</p>
              <p>Pedidos: {report.orders_upserted} | Itens: {report.order_items_inserted}</p>
              {report.errors.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-muted-foreground">
                    Ver erros ({report.errors.length})
                  </summary>
                  <ul className="mt-1 space-y-1 text-xs text-destructive">
                    {report.errors.slice(0, 10).map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}

          {state === "error" && (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <XCircle className="h-4 w-4 flex-shrink-0" />
              {errorMsg}
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => handleClose(false)}>
              Cancelar
            </Button>
            <Button
              onClick={handleImport}
              disabled={!file || state === "loading"}
            >
              {state === "loading" ? "Importando..." : "Importar"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
