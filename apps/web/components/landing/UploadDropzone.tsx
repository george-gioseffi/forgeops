"use client";

import React, { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, Zap, AlertTriangle, Loader2, Folder, CheckCircle2 } from "lucide-react";
import { analyzeDemo, analyzeUpload } from "@/lib/api";
import { cn } from "@/lib/utils";

type Phase = "idle" | "uploading" | "analyzing" | "done" | "error";

export function UploadDropzone() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const runUpload = useCallback(
    async (file: File) => {
      setError(null);
      setFileName(file.name);
      if (!file.name.toLowerCase().endsWith(".zip")) {
        setError("Envie um arquivo .zip.");
        setPhase("error");
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setError("Tamanho máximo é 50 MB. Tente um repositório menor.");
        setPhase("error");
        return;
      }

      setPhase("uploading");
      try {
        setPhase("analyzing");
        const session = await analyzeUpload(file);
        setPhase("done");
        router.push(`/analysis/${session.id}`);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Falha no envio.";
        setError(msg);
        setPhase("error");
      }
    },
    [router]
  );

  const runDemo = useCallback(async () => {
    setError(null);
    setFileName("samples/demo-repo");
    setPhase("analyzing");
    try {
      const session = await analyzeDemo();
      setPhase("done");
      router.push(`/analysis/${session.id}`);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Falha ao analisar.";
      setError(msg);
      setPhase("error");
    }
  }, [router]);

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) void runUpload(f);
  };

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) void runUpload(f);
  };

  const busy = phase === "uploading" || phase === "analyzing";

  return (
    <section id="inicio" className="mt-12">
      <div className="grid gap-4 lg:grid-cols-[1.25fr_1fr]">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            if (!busy) setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={busy ? undefined : onDrop}
          className={cn(
            "panel relative flex min-h-[280px] flex-col items-center justify-center gap-4 p-8 text-center transition-all",
            dragging && "border-violet-500/60 bg-violet-500/5",
            phase === "done" && "border-emerald-500/40"
          )}
        >
          <div
            className={cn(
              "inline-flex h-14 w-14 items-center justify-center rounded-2xl border transition-colors",
              phase === "done"
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
                : "border-violet-500/30 bg-violet-500/10 text-violet-200"
            )}
          >
            {busy ? (
              <Loader2 size={24} className="animate-spin" />
            ) : phase === "done" ? (
              <CheckCircle2 size={26} />
            ) : (
              <UploadCloud size={26} />
            )}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-zinc-100">
              {phase === "uploading" && "Enviando arquivo…"}
              {phase === "analyzing" && "Analisando repositório…"}
              {phase === "done" && "Análise pronta"}
              {(phase === "idle" || phase === "error") && "Arraste um ZIP do seu repositório"}
            </h3>
            <p className="mt-1.5 max-w-md text-sm text-zinc-400">
              {phase === "idle" && "Ou clique para escolher um arquivo. Máximo 50 MB."}
              {phase === "uploading" &&
                (fileName ? `Enviando ${fileName}…` : "Enviando o arquivo para o analisador…")}
              {phase === "analyzing" &&
                (fileName
                  ? `Inspecionando ${fileName} — classificando, pontuando e gerando relatórios.`
                  : "Varrendo árvore, classificando arquivos, pontuando e gerando relatórios.")}
              {phase === "done" && "Redirecionando para o painel de resultados…"}
              {phase === "error" && "Algo deu errado. Tente novamente abaixo."}
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2">
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              disabled={busy}
              className="btn-primary"
            >
              <UploadCloud size={16} />
              Escolher ZIP
            </button>
            <button
              type="button"
              onClick={runDemo}
              disabled={busy}
              className="btn-ghost"
            >
              <Zap size={16} />
              Analisar repositório demo
            </button>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".zip,application/zip,application/x-zip-compressed"
            className="hidden"
            onChange={onChange}
          />
          {error ? (
            <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-2 rounded-lg border border-rose-500/40 bg-rose-500/10 px-3 py-1.5 text-xs text-rose-200">
              <AlertTriangle size={14} />
              {error}
            </div>
          ) : null}
        </div>

        <aside className="panel flex flex-col justify-between p-6">
          <div>
            <div className="section-title">Ou comece pela demo</div>
            <h3 className="mt-2 text-lg font-semibold text-zinc-100">
              TaskForge — um repositório sintético cheio de problemas.
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-zinc-400">
              Embutido para entregar uma primeira análise relevante antes mesmo de qualquer upload.
              O ForgeOps vai apontar CI ausente, testes inexistentes, um{" "}
              <code className="rounded bg-bg-subtle px-1 text-violet-200">.env</code> commitado,
              documentação fraca e mais.
            </p>
          </div>
          <ul className="mt-5 space-y-2 text-sm text-zinc-400">
            <li className="flex items-center gap-2">
              <Folder size={14} className="text-violet-300" /> Backend Node/Express + cliente React
            </li>
            <li className="flex items-center gap-2">
              <Folder size={14} className="text-violet-300" /> Sem CI, sem testes, sem Docker — de propósito
            </li>
            <li className="flex items-center gap-2">
              <Folder size={14} className="text-violet-300" /> Artefatos de build commitados para realismo
            </li>
          </ul>
          <button
            type="button"
            onClick={runDemo}
            disabled={busy}
            className="btn-primary mt-6 w-full"
          >
            <Zap size={16} />
            Rodar análise da demo
          </button>
        </aside>
      </div>
    </section>
  );
}
