"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, RefreshCw } from "lucide-react";
import type { AnalysisSession } from "@/lib/types";
import { Tabs } from "@/components/ui/Tabs";
import { SummaryHero } from "./SummaryHero";
import { QuickMetrics } from "./QuickMetrics";
import { ScoreCards } from "./ScoreCards";
import { LanguageChart } from "./LanguageChart";
import { IssueSummaryChart } from "./IssueSummary";
import { StackPanel } from "./StackPanel";
import { IssueList } from "./IssueList";
import { PhasedPlan } from "./PhasedPlan";
import { RecommendationsPanel } from "./RecommendationsPanel";
import { DocsPreview } from "./DocsPreview";
import { MethodologyPanel } from "./MethodologyPanel";

const TABS = [
  { key: "overview", label: "Visão geral" },
  { key: "scores", label: "Notas" },
  { key: "issues", label: "Problemas" },
  { key: "plan", label: "Plano" },
  { key: "docs", label: "Relatórios" },
  { key: "methodology", label: "Metodologia" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export function AnalysisView({ session }: { session: AnalysisSession }) {
  const [tab, setTab] = useState<TabKey>("overview");
  const stats = session.repository_stats;
  const stack = session.detected_stack;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs text-zinc-400 hover:text-zinc-100"
        >
          <ArrowLeft size={14} /> Voltar ao dashboard
        </Link>
        <Link href="/" className="btn-ghost !px-4 !py-2 !text-xs">
          <RefreshCw size={14} /> Analisar outro repositório
        </Link>
      </div>

      <SummaryHero session={session} />
      <QuickMetrics session={session} />

      <div className="sticky top-[70px] z-30 -mx-6 border-y border-bg-border/60 bg-bg-base/85 px-6 py-3 backdrop-blur-md">
        <Tabs<TabKey> items={[...TABS]} active={tab} onChange={setTab} />
      </div>

      {tab === "overview" ? (
        <div className="space-y-8">
          <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
            {stats?.language_breakdown?.length ? (
              <LanguageChart data={stats.language_breakdown} />
            ) : null}
            <IssueSummaryChart issues={session.issues} />
          </div>
          {stack ? <StackPanel stack={stack} /> : null}
          <ScoreCards scores={session.scores} />
        </div>
      ) : null}

      {tab === "scores" ? (
        <div className="space-y-6">
          <ScoreCards scores={session.scores} />
          <MethodologyPanel scores={session.scores} />
        </div>
      ) : null}

      {tab === "issues" ? (
        <div className="space-y-6">
          <IssueList issues={session.issues} />
          <RecommendationsPanel recommendations={session.recommendations} />
        </div>
      ) : null}

      {tab === "plan" ? (
        <div className="space-y-6">
          <PhasedPlan phases={session.phases} />
          <RecommendationsPanel recommendations={session.recommendations} />
        </div>
      ) : null}

      {tab === "docs" ? <DocsPreview docs={session.generated_documents} /> : null}

      {tab === "methodology" ? <MethodologyPanel scores={session.scores} /> : null}
    </div>
  );
}
