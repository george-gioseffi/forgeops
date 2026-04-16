"use client";

import {
  BarChart,
  Bar,
  Cell,
  Tooltip,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from "recharts";
import type { IssueItem } from "@/lib/types";

const COLORS: Record<string, string> = {
  critical: "#fb7185",
  high: "#fb923c",
  medium: "#fbbf24",
  low: "#60a5fa",
};

export function IssueSummaryChart({ issues }: { issues: IssueItem[] }) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const i of issues) counts[i.severity] += 1;
  const data = [
    { name: "Crítico", key: "critical", value: counts.critical },
    { name: "Alto", key: "high", value: counts.high },
    { name: "Médio", key: "medium", value: counts.medium },
    { name: "Baixo", key: "low", value: counts.low },
  ];

  return (
    <div className="panel p-5">
      <div className="section-title">Severidade dos problemas</div>
      <h3 className="mt-1 text-lg font-semibold text-zinc-100">
        {issues.length} {issues.length === 1 ? "problema detectado" : "problemas detectados"}
      </h3>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, bottom: 0, left: 8 }}>
            <XAxis type="number" allowDecimals={false} tick={{ fill: "#9ca3af", fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: "#9ca3af", fontSize: 11 }}
              width={72}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "#161624",
                border: "1px solid #272739",
                borderRadius: 12,
                color: "#e9e9f4",
                fontSize: 12,
              }}
              formatter={(v: number) => [v, "Problemas"]}
            />
            <Bar dataKey="value" radius={[6, 6, 6, 6]}>
              {data.map((d) => (
                <Cell key={d.key} fill={COLORS[d.key]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
