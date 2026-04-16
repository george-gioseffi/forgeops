"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";
import type { IssueItem } from "@/lib/types";
import { cn, severityColor } from "@/lib/utils";

const SEV_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

const SEV_LABEL: Record<string, string> = {
  critical: "crítico",
  high: "alto",
  medium: "médio",
  low: "baixo",
};

function IssueRow({ issue }: { issue: IssueItem }) {
  const [open, setOpen] = useState(issue.severity === "critical" || issue.severity === "high");
  return (
    <li className="px-5 py-4">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-start gap-3 text-left"
        aria-expanded={open}
      >
        <span
          className={cn(
            "mt-0.5 inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider",
            severityColor(issue.severity)
          )}
        >
          <AlertTriangle size={10} />
          {SEV_LABEL[issue.severity] ?? issue.severity}
        </span>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-zinc-100">{issue.title}</span>
            <span className="text-[10px] uppercase tracking-wider text-zinc-500">
              {issue.category}
            </span>
            <span className="font-mono text-[10px] text-zinc-600">{issue.id}</span>
          </div>
          <p className="mt-1 text-sm text-zinc-400">{issue.description}</p>
        </div>
        {open ? (
          <ChevronUp size={14} className="mt-1 text-zinc-500" />
        ) : (
          <ChevronDown size={14} className="mt-1 text-zinc-500" />
        )}
      </button>
      {open ? (
        <div className="mt-3 space-y-3 rounded-xl border border-bg-border bg-bg-subtle/60 p-4 text-sm">
          {issue.evidence.length > 0 ? (
            <div>
              <div className="section-title">Evidências</div>
              <ul className="mt-2 space-y-1 text-zinc-300">
                {issue.evidence.map((ev, i) => (
                  <li key={i} className="font-mono text-xs text-zinc-400">
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          <div>
            <div className="section-title text-violet-300/80">Recomendação</div>
            <p className="mt-1.5 text-zinc-200">{issue.recommendation}</p>
          </div>
        </div>
      ) : null}
    </li>
  );
}

export function IssueList({ issues }: { issues: IssueItem[] }) {
  const [filter, setFilter] = useState<string>("all");
  const sorted = useMemo(() => {
    const base = [...issues].sort(
      (a, b) =>
        (SEV_ORDER[a.severity] ?? 9) - (SEV_ORDER[b.severity] ?? 9) ||
        a.category.localeCompare(b.category)
    );
    if (filter === "all") return base;
    return base.filter((i) => i.severity === filter);
  }, [issues, filter]);

  const filters: { key: string; label: string; n: number }[] = [
    { key: "all", label: "Todos", n: issues.length },
    { key: "critical", label: "Crítico", n: issues.filter((i) => i.severity === "critical").length },
    { key: "high", label: "Alto", n: issues.filter((i) => i.severity === "high").length },
    { key: "medium", label: "Médio", n: issues.filter((i) => i.severity === "medium").length },
    { key: "low", label: "Baixo", n: issues.filter((i) => i.severity === "low").length },
  ];

  return (
    <div className="panel">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-bg-border px-5 py-4">
        <div>
          <div className="section-title">Problemas diagnosticados</div>
          <h3 className="mt-1 text-lg font-semibold text-zinc-100">
            {issues.length} {issues.length === 1 ? "ocorrência com evidência" : "ocorrências com evidência"}
          </h3>
        </div>
        <div className="flex flex-wrap gap-1 rounded-xl border border-bg-border bg-bg-raised/60 p-1">
          {filters.map((f) => (
            <button
              key={f.key}
              type="button"
              onClick={() => setFilter(f.key)}
              className={cn("btn-tab", filter === f.key && "active")}
              disabled={f.n === 0}
            >
              {f.label}
              <span className="text-[10px] text-zinc-500">· {f.n}</span>
            </button>
          ))}
        </div>
      </div>
      {sorted.length === 0 ? (
        <div className="px-5 py-10 text-center text-sm text-zinc-500">
          Nenhum problema neste filtro.
        </div>
      ) : (
        <ul className="divide-y divide-bg-border">
          {sorted.map((issue) => (
            <IssueRow key={issue.id} issue={issue} />
          ))}
        </ul>
      )}
    </div>
  );
}
