import { ShieldAlert, ShieldCheck, TriangleAlert, CalendarClock, Boxes } from "lucide-react";
import type { AnalysisSession } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { gradeColor, scoreBand } from "@/lib/utils";

function RiskBadge({ risk }: { risk: "low" | "medium" | "high" }) {
  if (risk === "high")
    return (
      <Badge variant="danger">
        <ShieldAlert size={12} /> Risco alto
      </Badge>
    );
  if (risk === "medium")
    return (
      <Badge variant="warn">
        <TriangleAlert size={12} /> Risco médio
      </Badge>
    );
  return (
    <Badge variant="success">
      <ShieldCheck size={12} /> Risco baixo
    </Badge>
  );
}

export function SummaryHero({ session }: { session: AnalysisSession }) {
  const summary = session.summary;
  const stack = session.detected_stack;
  const grade = summary?.grade ?? "—";
  const overall = summary?.overall_score ?? 0;
  const band = scoreBand(overall);
  const dt = new Date(session.created_at);
  const sourceLabel = session.source_type === "upload" ? "Envio" : session.source_type === "demo" ? "Demo" : session.source_type;

  return (
    <section className="hero-bg relative overflow-hidden rounded-3xl border border-bg-border bg-bg-raised/60 p-6 sm:p-10">
      <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
        <CalendarClock size={14} />
        <span>{dt.toLocaleString("pt-BR")}</span>
        <span className="text-zinc-700">·</span>
        <span className="uppercase tracking-wider">{sourceLabel}</span>
        <span className="text-zinc-700">·</span>
        <span className="font-mono">{session.id}</span>
      </div>

      <div className="mt-4 flex flex-wrap items-end justify-between gap-6">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-50 sm:text-4xl">
            {session.repo_name}
          </h1>
          <p className="mt-3 text-base text-zinc-400 sm:text-lg">
            {summary?.headline ?? "Análise concluída."}
          </p>
          <div className="mt-5 flex flex-wrap items-center gap-2">
            {summary ? <RiskBadge risk={summary.risk_level} /> : null}
            {stack?.inferred_project_type ? (
              <Badge variant="accent">
                <Boxes size={12} /> {stack.inferred_project_type}
              </Badge>
            ) : null}
            {stack?.primary_languages?.slice(0, 3).map((l) => (
              <Badge key={l}>{l}</Badge>
            ))}
            {stack?.frameworks?.slice(0, 4).map((f) => (
              <Badge key={f} variant="outline">
                {f}
              </Badge>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-6 rounded-2xl border border-bg-border bg-bg-card/80 px-6 py-4 shadow-panel">
          <div className="text-center">
            <div className={`font-mono text-5xl leading-none tabular-nums ${gradeColor(grade)}`}>
              {grade}
            </div>
            <div className="mt-2 text-[11px] uppercase tracking-[0.18em] text-zinc-500">
              Nota
            </div>
          </div>
          <div className="h-12 w-px bg-bg-border" />
          <div>
            <div className={`text-4xl font-semibold leading-none tabular-nums ${band.className}`}>
              {overall}
              <span className="text-base text-zinc-500">/100</span>
            </div>
            <div className="mt-2 text-[11px] uppercase tracking-[0.18em] text-zinc-500">
              Geral · {band.label}
            </div>
          </div>
        </div>
      </div>

      {summary && (summary.strengths.length > 0 || summary.weaknesses.length > 0) ? (
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          {summary.strengths.length > 0 ? (
            <div className="panel bg-bg-card/70 p-4">
              <div className="section-title text-emerald-300/80">Pontos fortes</div>
              <ul className="mt-2 space-y-1.5 text-sm text-zinc-300">
                {summary.strengths.map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mt-1 block h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {summary.weaknesses.length > 0 ? (
            <div className="panel bg-bg-card/70 p-4">
              <div className="section-title text-rose-300/80">Pontos frágeis</div>
              <ul className="mt-2 space-y-1.5 text-sm text-zinc-300">
                {summary.weaknesses.map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="mt-1 block h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
