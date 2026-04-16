import { Flag } from "lucide-react";
import type { PlanPhase } from "@/lib/types";
import { cn } from "@/lib/utils";

const RISK_TONE: Record<string, string> = {
  low: "border-emerald-500/30 text-emerald-300 bg-emerald-500/10",
  medium: "border-amber-500/30 text-amber-300 bg-amber-500/10",
  high: "border-rose-500/30 text-rose-300 bg-rose-500/10",
};

const RISK_LABEL: Record<string, string> = {
  low: "baixo",
  medium: "médio",
  high: "alto",
};

const EFFORT_LABEL: Record<string, string> = {
  small: "pequeno",
  medium: "médio",
  large: "grande",
};

const IMPACT_LABEL: Record<string, string> = {
  low: "baixo",
  medium: "médio",
  high: "alto",
};

const EFFORT_TONE: Record<string, string> = {
  small: "text-zinc-400",
  medium: "text-zinc-300",
  large: "text-zinc-100",
};

export function PhasedPlan({ phases }: { phases: PlanPhase[] }) {
  if (!phases?.length) return null;
  return (
    <div className="panel">
      <div className="flex items-center justify-between border-b border-bg-border px-5 py-4">
        <div>
          <div className="section-title">Plano de execução</div>
          <h3 className="mt-1 text-lg font-semibold text-zinc-100">
            Roteiro de remediação em {phases.length} fases
          </h3>
        </div>
        <div className="text-xs text-zinc-500">
          As fases estão ordenadas para que vitórias iniciais destravem o trabalho seguinte.
        </div>
      </div>
      <ol className="divide-y divide-bg-border">
        {phases.map((p) => (
          <li key={p.phase} className="grid gap-4 px-5 py-5 sm:grid-cols-[auto_1fr]">
            <div className="flex items-start gap-3 sm:w-40">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-violet-500/30 bg-violet-500/10 font-mono text-sm text-violet-200">
                {p.phase.toString().padStart(2, "0")}
              </span>
              <div>
                <div className="text-xs font-mono tracking-widest text-violet-300">
                  FASE {p.phase}
                </div>
                <div className="mt-0.5 text-sm font-semibold text-zinc-100">
                  {p.title}
                </div>
              </div>
            </div>
            <div>
              <p className="text-sm text-zinc-400">{p.goal}</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                <span
                  className={cn(
                    "rounded-full border px-2.5 py-0.5 text-[11px]",
                    RISK_TONE[p.risk]
                  )}
                >
                  <Flag size={10} className="-mt-0.5 mr-1 inline" />
                  risco {RISK_LABEL[p.risk] ?? p.risk}
                </span>
                <span className="rounded-full border border-bg-border bg-bg-subtle px-2.5 py-0.5 text-[11px] text-zinc-300">
                  esforço {EFFORT_LABEL[p.effort] ?? p.effort}
                </span>
                <span className="rounded-full border border-bg-border bg-bg-subtle px-2.5 py-0.5 text-[11px] text-zinc-300">
                  impacto {IMPACT_LABEL[p.impact] ?? p.impact}
                </span>
              </div>
              {p.tasks.length > 0 ? (
                <ul className="mt-4 space-y-2">
                  {p.tasks.map((task, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-3 rounded-lg border border-bg-border bg-bg-subtle/40 px-3 py-2"
                    >
                      <span
                        className={cn(
                          "mt-1 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md border border-bg-border bg-bg-base font-mono text-[10px] font-semibold",
                          EFFORT_TONE[
                            task.effort === "S" ? "small" : task.effort === "L" ? "large" : "medium"
                          ]
                        )}
                      >
                        {task.effort}
                      </span>
                      <div className="text-sm">
                        <div className="font-medium text-zinc-100">{task.title}</div>
                        <div className="mt-0.5 text-zinc-400">{task.detail}</div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
