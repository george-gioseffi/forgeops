import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return "—";
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB", "TB"];
  let value = bytes / 1024;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i++;
  }
  return `${value.toFixed(value >= 100 ? 0 : value >= 10 ? 1 : 2)} ${units[i]}`;
}

export function formatNumber(n: number): string {
  if (!Number.isFinite(n)) return "—";
  return new Intl.NumberFormat("pt-BR").format(Math.round(n));
}

export function formatRelativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  if (!Number.isFinite(then)) return iso;
  const diffMs = Date.now() - then;
  const diffMin = Math.max(0, Math.round(diffMs / 60000));
  if (diffMin < 1) return "agora mesmo";
  if (diffMin < 60) return `há ${diffMin} min`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `há ${diffHr}h`;
  const diffDay = Math.round(diffHr / 24);
  if (diffDay < 30) return `há ${diffDay}d`;
  return new Date(iso).toLocaleDateString("pt-BR");
}

const GRADE_COLORS: Record<string, string> = {
  "A+": "text-emerald-300",
  A: "text-emerald-300",
  B: "text-teal-300",
  C: "text-amber-300",
  D: "text-orange-300",
  F: "text-rose-300",
};

export function gradeColor(grade: string): string {
  return GRADE_COLORS[grade] ?? "text-zinc-300";
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  high: "bg-orange-500/15 text-orange-300 border-orange-500/30",
  medium: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  low: "bg-sky-500/15 text-sky-300 border-sky-500/30",
};

export function severityColor(severity: string): string {
  return SEVERITY_COLORS[severity] ?? "bg-zinc-500/15 text-zinc-300 border-zinc-500/30";
}

const PRIORITY_COLORS: Record<string, string> = {
  now: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  next: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  later: "bg-sky-500/15 text-sky-300 border-sky-500/30",
};

export function priorityColor(priority: string): string {
  return PRIORITY_COLORS[priority] ?? "bg-zinc-500/15 text-zinc-300 border-zinc-500/30";
}

export function scoreBand(score: number): { label: string; className: string } {
  if (score >= 85) return { label: "Excelente", className: "text-emerald-300" };
  if (score >= 70) return { label: "Saudável", className: "text-teal-300" };
  if (score >= 55) return { label: "Precisa melhorar", className: "text-amber-300" };
  if (score >= 40) return { label: "Fraco", className: "text-orange-300" };
  return { label: "Crítico", className: "text-rose-300" };
}
