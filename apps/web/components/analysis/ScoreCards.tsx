"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { ScoreDimension } from "@/lib/types";
import { scoreBand } from "@/lib/utils";
import { ProgressBar } from "@/components/ui/Progress";

function ScoreCard({ score }: { score: ScoreDimension }) {
  const [open, setOpen] = useState(false);
  const band = scoreBand(score.score);
  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-[11px] uppercase tracking-wider text-zinc-500">
            {score.name}
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-3xl font-semibold tabular-nums ${band.className}`}>
              {score.score}
            </span>
            <span className="text-sm text-zinc-500">/ 100</span>
          </div>
          <div className="mt-1 text-xs text-zinc-500">
            {band.label} · peso {Math.round(score.weight * 100)}%
          </div>
        </div>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="text-xs text-zinc-400 hover:text-zinc-100 inline-flex items-center gap-1"
          aria-expanded={open}
        >
          {open ? "Ocultar" : "Por quê"}
          {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
      </div>
      <div className="mt-4">
        <ProgressBar value={score.score} />
      </div>

      {open ? (
        <div className="mt-4 space-y-3 text-sm">
          <p className="text-zinc-400">{score.rationale}</p>
          {score.positives.length > 0 ? (
            <div>
              <div className="section-title text-emerald-300/80">Pontos positivos</div>
              <ul className="mt-2 space-y-1 text-zinc-300">
                {score.positives.map((p, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mt-1 block h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {score.concerns.length > 0 ? (
            <div>
              <div className="section-title text-rose-300/80">Preocupações</div>
              <ul className="mt-2 space-y-1 text-zinc-300">
                {score.concerns.map((p, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mt-1 block h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {score.recommendations.length > 0 ? (
            <div>
              <div className="section-title text-violet-300/80">Recomendações</div>
              <ul className="mt-2 space-y-1 text-zinc-300">
                {score.recommendations.map((p, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mt-1 block h-1.5 w-1.5 shrink-0 rounded-full bg-violet-400" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

export function ScoreCards({ scores }: { scores: ScoreDimension[] }) {
  if (!scores?.length) return null;
  return (
    <section className="mt-8">
      <div className="mb-4 flex items-end justify-between">
        <div>
          <div className="section-title">Saúde de engenharia</div>
          <h2 className="mt-2 text-xl font-semibold text-zinc-100">Detalhamento das notas</h2>
        </div>
        <div className="text-xs text-zinc-500">
          Ponderado em 7 dimensões · clique em <span className="text-zinc-300">Por quê</span> para ver evidências.
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {scores.map((s) => (
          <ScoreCard key={s.key} score={s} />
        ))}
      </div>
    </section>
  );
}
