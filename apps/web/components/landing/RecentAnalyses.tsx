"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Clock, ArrowRight } from "lucide-react";
import { fetchRecentAnalyses } from "@/lib/api";
import { formatRelativeTime, gradeColor } from "@/lib/utils";
import type { RecentAnalysis } from "@/lib/types";

const SOURCE_LABEL: Record<string, string> = {
  upload: "Envio",
  demo: "Demo",
};

export function RecentAnalyses() {
  const [items, setItems] = useState<RecentAnalysis[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetchRecentAnalyses().then((list) => {
      if (!cancelled) setItems(list);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  if (items === null || items.length === 0) return null;

  return (
    <section className="mt-24">
      <div className="mb-6 flex items-end justify-between">
        <div>
          <div className="section-title">Atividade recente</div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-100 sm:text-3xl">
            Suas últimas análises
          </h2>
        </div>
      </div>
      <div className="panel overflow-hidden">
        <ul className="divide-y divide-bg-border">
          {items.slice(0, 6).map((item) => (
            <li key={item.id}>
              <Link
                href={`/analysis/${item.id}`}
                className="group flex items-center justify-between gap-4 px-5 py-3.5 transition-colors hover:bg-bg-subtle/40"
              >
                <div className="flex min-w-0 items-center gap-4">
                  <div
                    className={`font-mono text-lg tabular-nums ${gradeColor(
                      item.grade ?? ""
                    )}`}
                  >
                    {item.grade ?? "—"}
                  </div>
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-zinc-100">
                      {item.repo_name}
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-[11px] text-zinc-500">
                      <Clock size={11} />
                      {formatRelativeTime(item.created_at)}
                      <span className="text-zinc-600">·</span>
                      {SOURCE_LABEL[item.source_type] ?? item.source_type}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="hidden text-xs text-zinc-400 sm:block">
                    {item.overall !== null ? `${item.overall}/100` : ""}
                  </div>
                  <ArrowRight
                    size={16}
                    className="text-zinc-500 transition-transform group-hover:translate-x-0.5 group-hover:text-violet-300"
                  />
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
