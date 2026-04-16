"use client";

import { useMemo, useState } from "react";
import { Download, FileText } from "lucide-react";
import type { GeneratedDocument } from "@/lib/types";
import { cn } from "@/lib/utils";
import { RenderMarkdown } from "@/lib/markdown";

export function DocsPreview({ docs }: { docs: GeneratedDocument[] }) {
  const [active, setActive] = useState<string>(docs[0]?.slug ?? "");

  const doc = useMemo(
    () => docs.find((d) => d.slug === active) ?? docs[0],
    [docs, active]
  );

  if (!doc) return null;

  const download = (d: GeneratedDocument) => {
    const blob = new Blob([d.content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${d.slug}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="panel overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-bg-border px-5 py-4">
        <div>
          <div className="section-title">Documentação gerada</div>
          <h3 className="mt-1 text-lg font-semibold text-zinc-100">
            {docs.length} {docs.length === 1 ? "relatório" : "relatórios"} em Markdown
          </h3>
        </div>
        <button
          type="button"
          onClick={() => download(doc)}
          className="btn-ghost !px-4 !py-2 !text-xs"
        >
          <Download size={14} />
          Baixar {doc.slug}.md
        </button>
      </div>
      <div className="grid lg:grid-cols-[220px_1fr]">
        <div className="border-b border-bg-border p-3 lg:border-b-0 lg:border-r">
          <ul className="flex flex-row gap-1 overflow-x-auto lg:flex-col">
            {docs.map((d) => (
              <li key={d.slug}>
                <button
                  type="button"
                  onClick={() => setActive(d.slug)}
                  className={cn(
                    "flex w-full items-center gap-2 whitespace-nowrap rounded-lg border border-transparent px-3 py-2 text-left text-sm text-zinc-400 transition-colors hover:text-zinc-100",
                    d.slug === active &&
                      "border-violet-500/30 bg-violet-500/10 text-white"
                  )}
                >
                  <FileText size={14} />
                  {d.title}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="max-h-[640px] overflow-y-auto p-6">
          <RenderMarkdown content={doc.content} />
        </div>
      </div>
    </div>
  );
}
