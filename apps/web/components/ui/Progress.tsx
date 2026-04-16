import React from "react";
import { cn } from "@/lib/utils";

export function ProgressBar({
  value,
  className,
  track = "bg-bg-subtle",
  tone,
}: {
  value: number;
  className?: string;
  track?: string;
  tone?: string;
}) {
  const pct = Math.max(0, Math.min(100, value));
  const fillTone =
    tone ??
    (pct >= 80
      ? "bg-emerald-400"
      : pct >= 65
      ? "bg-teal-400"
      : pct >= 50
      ? "bg-amber-400"
      : pct >= 35
      ? "bg-orange-400"
      : "bg-rose-400");
  return (
    <div className={cn("h-2 w-full rounded-full overflow-hidden", track, className)}>
      <div
        className={cn("h-full rounded-full transition-all duration-500", fillTone)}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
