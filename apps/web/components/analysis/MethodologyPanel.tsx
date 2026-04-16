import Link from "next/link";
import { BookOpen } from "lucide-react";
import type { ScoreDimension } from "@/lib/types";

export function MethodologyPanel({ scores }: { scores: ScoreDimension[] }) {
  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="section-title">Metodologia</div>
          <h3 className="mt-1 text-lg font-semibold text-zinc-100">
            Como essas notas foram calculadas
          </h3>
          <p className="mt-2 max-w-3xl text-sm text-zinc-400">
            Cada dimensão é um agregado ponderado de heurísticas determinísticas sobre
            arquivos, manifestos e a forma do repositório. Sem ML, sem chamadas externas.
            Toda nota traz seus próprios pontos positivos, preocupações e recomendações —
            clique em <span className="text-zinc-300">Por quê</span> no card para ver as
            evidências.
          </p>
        </div>
        <Link
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost !px-4 !py-2 !text-xs"
        >
          <BookOpen size={14} /> Documentação do scoring
        </Link>
      </div>
      <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {scores.map((s) => (
          <div key={s.key} className="rounded-lg border border-bg-border bg-bg-subtle/50 p-3">
            <div className="flex items-baseline justify-between">
              <div className="text-sm font-medium text-zinc-100">{s.name}</div>
              <div className="font-mono text-xs text-zinc-400">
                peso {Math.round(s.weight * 100)}%
              </div>
            </div>
            <p className="mt-1 text-xs text-zinc-500">{s.rationale}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
