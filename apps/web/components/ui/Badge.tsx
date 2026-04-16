import React from "react";
import { cn } from "@/lib/utils";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  variant?: "default" | "accent" | "outline" | "warn" | "danger" | "success";
};

const STYLES: Record<NonNullable<BadgeProps["variant"]>, string> = {
  default: "bg-bg-subtle text-zinc-300 border-bg-border",
  accent: "bg-violet-500/15 text-violet-200 border-violet-500/30",
  outline: "bg-transparent text-zinc-300 border-bg-border",
  warn: "bg-amber-500/15 text-amber-200 border-amber-500/30",
  danger: "bg-rose-500/15 text-rose-200 border-rose-500/30",
  success: "bg-emerald-500/15 text-emerald-200 border-emerald-500/30",
};

export function Badge({ variant = "default", className, ...rest }: BadgeProps) {
  return (
    <span
      {...rest}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
        STYLES[variant],
        className
      )}
    />
  );
}
