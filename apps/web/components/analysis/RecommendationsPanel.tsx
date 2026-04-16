import type { RecommendationItem } from "@/lib/types";
import { priorityColor, cn } from "@/lib/utils";

const PRIORITY_LABEL: Record<string, string> = {
  now: "Fazer agora",
  next: "Fazer em seguida",
  later: "Fazer depois",
};

const IMPACT_LABEL: Record<string, string> = {
  high: "alto",
  medium: "médio",
  low: "baixo",
};

const IMPACT_DOT: Record<string, string> = {
  high: "bg-rose-400",
  medium: "bg-amber-400",
  low: "bg-sky-400",
};

export function RecommendationsPanel({
  recommendations,
}: {
  recommendations: RecommendationItem[];
}) {
  if (!recommendations?.length) return null;
  const groups: Record<string, RecommendationItem[]> = { now: [], next: [], later: [] };
  for (const r of recommendations) groups[r.priority]?.push(r);

  return (
    <div className="panel">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-bg-border px-5 py-4">
        <div>
          <div className="section-title">Recomendações priorizadas</div>
          <h3 className="mt-1 text-lg font-semibold text-zinc-100">
            {recommendations.length} {recommendations.length === 1 ? "ação" : "ações"} agrupadas por urgência
          </h3>
        </div>
      </div>

      <div className="grid gap-4 p-5 md:grid-cols-3">
        {(["now", "next", "later"] as const).map((prio) => (
          <div key={prio} className="flex flex-col gap-3">
            <div
              className={cn(
                "inline-flex items-center gap-1 self-start rounded-full border px-2.5 py-1 text-xs font-medium",
                priorityColor(prio)
              )}
            >
              {PRIORITY_LABEL[prio]} · {groups[prio].length}
            </div>
            <ul className="space-y-2">
              {groups[prio].length === 0 ? (
                <li className="rounded-lg border border-dashed border-bg-border px-3 py-4 text-center text-xs text-zinc-600">
                  Nada por aqui.
                </li>
              ) : (
                groups[prio].map((rec) => (
                  <li
                    key={rec.id}
                    className="rounded-lg border border-bg-border bg-bg-subtle/50 px-3 py-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="text-sm font-medium text-zinc-100">
                        {rec.title}
                      </div>
                      <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider text-zinc-500">
                        <span
                          className={cn("h-1.5 w-1.5 rounded-full", IMPACT_DOT[rec.impact])}
                        />
                        {IMPACT_LABEL[rec.impact] ?? rec.impact}
                      </span>
                    </div>
                    <p className="mt-1 text-xs leading-relaxed text-zinc-400">
                      {rec.rationale}
                    </p>
                    <div className="mt-2 text-[10px] font-mono text-zinc-600">
                      esforço: {rec.effort}
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
