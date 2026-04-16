import React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("forge-pulse rounded-lg bg-bg-subtle", className)} aria-hidden />
  );
}
