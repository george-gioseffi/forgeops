import {
  Cpu,
  Code2,
  Database,
  Wrench,
  Boxes,
  GitBranch,
  Package,
  FlaskConical,
} from "lucide-react";
import type { DetectedStack } from "@/lib/types";

const ROWS: { label: string; icon: typeof Cpu; field: keyof DetectedStack }[] = [
  { label: "Linguagens", icon: Code2, field: "primary_languages" },
  { label: "Frontend", icon: Cpu, field: "probable_frontend" },
  { label: "Backend", icon: Cpu, field: "probable_backend" },
  { label: "Frameworks", icon: Boxes, field: "frameworks" },
  { label: "Bancos de dados", icon: Database, field: "databases" },
  { label: "Testes", icon: FlaskConical, field: "testing_tools" },
  { label: "CI", icon: GitBranch, field: "ci_tools" },
  { label: "Containers", icon: Wrench, field: "containerization" },
  { label: "Gerenciadores", icon: Package, field: "package_managers" },
];

export function StackPanel({ stack }: { stack: DetectedStack }) {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div>
          <div className="section-title">Stack detectada</div>
          <h3 className="mt-1 text-lg font-semibold text-zinc-100">
            {stack.inferred_project_type}
          </h3>
        </div>
      </div>
      <dl className="mt-5 divide-y divide-bg-border">
        {ROWS.map(({ label, icon: Icon, field }) => {
          const values = (stack[field] ?? []) as string[];
          return (
            <div
              key={label}
              className="flex items-start gap-4 py-3 text-sm"
            >
              <dt className="flex w-36 shrink-0 items-center gap-2 text-zinc-400">
                <Icon size={14} className="text-violet-300" />
                {label}
              </dt>
              <dd className="flex flex-wrap gap-1.5">
                {values.length > 0 ? (
                  values.map((v) => (
                    <span key={v} className="chip">
                      {v}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-zinc-600">—</span>
                )}
              </dd>
            </div>
          );
        })}
      </dl>
    </div>
  );
}
