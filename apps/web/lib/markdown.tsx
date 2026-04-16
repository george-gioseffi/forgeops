// Minimal, safe markdown renderer — no external deps.
// Supports: headings, paragraphs, bulleted + numbered lists, code fences,
// inline code, bold, italics, links, horizontal rules, blockquotes, tables.

import React from "react";

type Block =
  | { type: "heading"; level: number; text: string }
  | { type: "paragraph"; text: string }
  | { type: "list"; ordered: boolean; items: string[] }
  | { type: "code"; lang: string; text: string }
  | { type: "hr" }
  | { type: "blockquote"; text: string }
  | { type: "table"; headers: string[]; rows: string[][] };

function splitBlocks(src: string): Block[] {
  const lines = src.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    // Fenced code
    if (/^```/.test(line)) {
      const lang = line.replace(/^```/, "").trim();
      const start = ++i;
      while (i < lines.length && !/^```/.test(lines[i])) i++;
      blocks.push({ type: "code", lang, text: lines.slice(start, i).join("\n") });
      i++; // consume closing fence
      continue;
    }
    if (!line.trim()) {
      i++;
      continue;
    }
    // Heading
    const heading = /^(#{1,6})\s+(.*)$/.exec(line);
    if (heading) {
      blocks.push({
        type: "heading",
        level: heading[1].length,
        text: heading[2].trim(),
      });
      i++;
      continue;
    }
    // Horizontal rule
    if (/^\s*---+\s*$/.test(line)) {
      blocks.push({ type: "hr" });
      i++;
      continue;
    }
    // Blockquote (single line for simplicity)
    if (/^>\s?/.test(line)) {
      const text = line.replace(/^>\s?/, "");
      blocks.push({ type: "blockquote", text });
      i++;
      continue;
    }
    // Table: "| ... |" followed by separator
    if (/^\s*\|.*\|\s*$/.test(line) && /^\s*\|?[\s\-|:]+\|?\s*$/.test(lines[i + 1] ?? "")) {
      const headers = line
        .trim()
        .replace(/^\||\|$/g, "")
        .split("|")
        .map((s) => s.trim());
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) {
        const row = lines[i].trim().replace(/^\||\|$/g, "").split("|").map((s) => s.trim());
        rows.push(row);
        i++;
      }
      blocks.push({ type: "table", headers, rows });
      continue;
    }
    // List (bulleted or ordered)
    if (/^\s*([*\-+])\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      const items: string[] = [];
      while (
        i < lines.length &&
        (/^\s*([*\-+])\s+/.test(lines[i]) || /^\s*\d+\.\s+/.test(lines[i]))
      ) {
        items.push(lines[i].replace(/^\s*([*\-+]|\d+\.)\s+/, "").trim());
        i++;
      }
      blocks.push({ type: "list", ordered, items });
      continue;
    }
    // Paragraph: join adjacent non-blank, non-special lines
    const paraLines = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() &&
      !/^#{1,6}\s+/.test(lines[i]) &&
      !/^```/.test(lines[i]) &&
      !/^\s*([*\-+])\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i]) &&
      !/^\s*---+\s*$/.test(lines[i]) &&
      !/^>\s?/.test(lines[i]) &&
      !/^\s*\|.*\|\s*$/.test(lines[i])
    ) {
      paraLines.push(lines[i]);
      i++;
    }
    blocks.push({ type: "paragraph", text: paraLines.join(" ") });
  }
  return blocks;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderInline(text: string): string {
  // Already escaped input expected
  let out = escapeHtml(text);
  // Links: [label](url) — restrict to http(s) and relative
  out = out.replace(
    /\[([^\]]+)\]\(((?:https?:\/\/|\/|\.\/|#)[^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  );
  // Inline code
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Bold then italics
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  out = out.replace(/_([^_]+)_/g, "<em>$1</em>");
  return out;
}

function blockKey(block: Block, index: number): string {
  switch (block.type) {
    case "heading":
      return `h-${index}-${block.level}`;
    case "paragraph":
      return `p-${index}`;
    case "list":
      return `l-${index}-${block.ordered ? "ol" : "ul"}`;
    case "code":
      return `c-${index}`;
    case "hr":
      return `hr-${index}`;
    case "blockquote":
      return `bq-${index}`;
    case "table":
      return `t-${index}`;
  }
}

export function RenderMarkdown({ content }: { content: string }): React.ReactElement {
  const blocks = splitBlocks(content);
  return (
    <div className="prose-mini">
      {blocks.map((block, index) => {
        const key = blockKey(block, index);
        switch (block.type) {
          case "heading": {
            const Tag = (`h${Math.min(block.level, 6)}` as unknown) as keyof JSX.IntrinsicElements;
            return (
              <Tag key={key} dangerouslySetInnerHTML={{ __html: renderInline(block.text) }} />
            );
          }
          case "paragraph":
            return (
              <p key={key} dangerouslySetInnerHTML={{ __html: renderInline(block.text) }} />
            );
          case "list": {
            const ListTag = block.ordered ? "ol" : "ul";
            return (
              <ListTag key={key}>
                {block.items.map((item, iidx) => (
                  <li
                    key={`${key}-${iidx}`}
                    dangerouslySetInnerHTML={{ __html: renderInline(item) }}
                  />
                ))}
              </ListTag>
            );
          }
          case "code":
            return (
              <pre key={key}>
                <code>{block.text}</code>
              </pre>
            );
          case "hr":
            return <hr key={key} />;
          case "blockquote":
            return (
              <blockquote
                key={key}
                dangerouslySetInnerHTML={{ __html: renderInline(block.text) }}
              />
            );
          case "table":
            return (
              <table key={key}>
                <thead>
                  <tr>
                    {block.headers.map((h, hi) => (
                      <th
                        key={`${key}-h-${hi}`}
                        dangerouslySetInnerHTML={{ __html: renderInline(h) }}
                      />
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {block.rows.map((row, ri) => (
                    <tr key={`${key}-r-${ri}`}>
                      {row.map((c, ci) => (
                        <td
                          key={`${key}-r-${ri}-c-${ci}`}
                          dangerouslySetInnerHTML={{ __html: renderInline(c) }}
                        />
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            );
        }
      })}
    </div>
  );
}
