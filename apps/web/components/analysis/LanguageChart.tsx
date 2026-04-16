"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { LanguageBreakdown } from "@/lib/types";
import { formatBytes } from "@/lib/utils";

const COLORS = [
  "#8a68ff",
  "#5a2feb",
  "#b399ff",
  "#7c4dff",
  "#a78bfa",
  "#c4b5fd",
  "#ddd6fe",
  "#4c1d95",
];

export function LanguageChart({ data }: { data: LanguageBreakdown[] }) {
  if (!data?.length) return null;
  const top = data.slice(0, 8).map((d) => ({
    name: d.language,
    value: d.bytes,
    files: d.files,
    share: d.share,
  }));

  return (
    <div className="panel p-5">
      <div className="section-title">Composição de linguagens</div>
      <h3 className="mt-1 text-lg font-semibold text-zinc-100">
        Top {top.length} linguagens por tamanho
      </h3>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={top}
              dataKey="value"
              nameKey="name"
              innerRadius={50}
              outerRadius={90}
              stroke="#0a0a12"
              strokeWidth={2}
            >
              {top.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#161624",
                border: "1px solid #272739",
                borderRadius: 12,
                color: "#e9e9f4",
                fontSize: 12,
              }}
              formatter={(value: number, _name: string, item) => [
                `${formatBytes(value)} · ${item?.payload?.files ?? 0} arquivos`,
                item?.payload?.name ?? "",
              ]}
            />
            <Legend
              verticalAlign="bottom"
              iconType="circle"
              wrapperStyle={{ fontSize: 11, color: "#9ca3af" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
