import type { AnalysisSession } from "@/lib/types";
import { formatBytes, formatNumber } from "@/lib/utils";

export function QuickMetrics({ session }: { session: AnalysisSession }) {
  const stats = session.repository_stats;
  if (!stats) return null;

  const items: { label: string; value: string }[] = [
    { label: "Arquivos", value: formatNumber(stats.total_files) },
    { label: "Código", value: formatNumber(stats.code_files) },
    { label: "Diretórios", value: formatNumber(stats.total_directories) },
    { label: "Tamanho", value: formatBytes(stats.total_size_bytes) },
    { label: "Profundidade", value: String(stats.max_depth) },
    { label: "Testes", value: formatNumber(stats.test_files.length) },
    { label: "Docs", value: formatNumber(stats.docs_files.length) },
    { label: "CI", value: formatNumber(stats.ci_files.length) },
    { label: "Container", value: formatNumber(stats.container_files.length) },
    { label: "Grandes >1MB", value: formatNumber(stats.large_files_count) },
  ];

  return (
    <section className="mt-6 grid grid-cols-2 gap-2.5 sm:grid-cols-4 lg:grid-cols-5">
      {items.map((i) => (
        <div key={i.label} className="stat-card">
          <div className="text-[10px] uppercase tracking-[0.16em] text-zinc-500">
            {i.label}
          </div>
          <div className="mt-1.5 text-xl font-semibold tabular-nums text-zinc-100">
            {i.value}
          </div>
        </div>
      ))}
    </section>
  );
}
