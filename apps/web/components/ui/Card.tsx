import React from "react";
import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  ...rest
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...rest}
      className={cn(
        "rounded-2xl border border-bg-border bg-bg-card shadow-panel",
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  className,
  children,
  ...rest
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      {...rest}
      className={cn(
        "flex flex-wrap items-start justify-between gap-3 border-b border-bg-border px-5 py-4",
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardTitle({
  className,
  children,
  ...rest
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      {...rest}
      className={cn("text-sm font-semibold tracking-wide text-zinc-100", className)}
    >
      {children}
    </h3>
  );
}

export function CardBody({
  className,
  children,
  ...rest
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div {...rest} className={cn("px-5 py-5", className)}>
      {children}
    </div>
  );
}
