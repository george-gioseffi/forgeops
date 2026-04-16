"use client";

import React from "react";
import { cn } from "@/lib/utils";

export type TabItem<K extends string = string> = {
  key: K;
  label: string;
  hint?: string;
};

export function Tabs<K extends string>({
  items,
  active,
  onChange,
  className,
}: {
  items: TabItem<K>[];
  active: K;
  onChange: (key: K) => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-1 rounded-xl border border-bg-border bg-bg-raised/60 p-1",
        className
      )}
    >
      {items.map((item) => {
        const isActive = item.key === active;
        return (
          <button
            key={item.key}
            type="button"
            onClick={() => onChange(item.key)}
            className={cn(
              "btn-tab",
              isActive && "active"
            )}
            aria-pressed={isActive}
          >
            {item.label}
            {item.hint ? (
              <span className="text-[10px] text-zinc-500">{item.hint}</span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
