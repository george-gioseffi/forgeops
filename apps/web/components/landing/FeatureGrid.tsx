import {
  FileSearch,
  GaugeCircle,
  ShieldAlert,
  ListChecks,
  FileText,
  Activity,
} from "lucide-react";

const FEATURES = [
  {
    title: "Varredura completa",
    desc: "Percorre a árvore e classifica cada arquivo por linguagem, papel e risco.",
    icon: FileSearch,
  },
  {
    title: "Pontuação em 7 eixos",
    desc: "Arquitetura, Manutenibilidade, Documentação, Testes, Entrega, Segurança, Limpeza.",
    icon: GaugeCircle,
  },
  {
    title: "Problemas com evidência",
    desc: "Toda ocorrência aponta o arquivo ou sinal que a disparou. Nada inventado.",
    icon: ShieldAlert,
  },
  {
    title: "Plano em fases",
    desc: "Cinco etapas encadeadas — as vitórias iniciais destravam o trabalho seguinte.",
    icon: ListChecks,
  },
  {
    title: "Relatórios gerados",
    desc: "Visão geral, arquitetura, dívida técnica e plano de ação — Markdown pronto para baixar.",
    icon: FileText,
  },
  {
    title: "Determinístico",
    desc: "Regras heurísticas. Sem chaves de API. Tudo roda na sua máquina.",
    icon: Activity,
  },
];

export function FeatureGrid() {
  return (
    <section className="mt-24">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <div className="section-title">O que o ForgeOps entrega</div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-100 sm:text-3xl">
            Uma auditoria que lê como a revisão de um engenheiro sênior.
          </h2>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f) => {
          const Icon = f.icon;
          return (
            <div key={f.title} className="panel-hoverable group p-5">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-violet-500/30 bg-violet-500/10 text-violet-200 transition-colors group-hover:bg-violet-500/15">
                  <Icon size={18} />
                </span>
                <h3 className="text-sm font-semibold text-zinc-100">{f.title}</h3>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-zinc-400">{f.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
