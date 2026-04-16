import { FolderTree, Scale, FileStack, LineChart } from "lucide-react";

const STEPS = [
  {
    num: "01",
    icon: FolderTree,
    title: "Varrer e classificar",
    body: "Percorre a árvore e classifica cada arquivo por linguagem e papel (código, teste, documentação, CI, container, env). Detecta manifestos e a forma do projeto.",
  },
  {
    num: "02",
    icon: Scale,
    title: "Pontuar e ponderar",
    body: "Sete dimensões com pesos fixos. Cada nota é justificada por heurísticas atribuíveis, com pontos fortes e preocupações anexados.",
  },
  {
    num: "03",
    icon: LineChart,
    title: "Diagnosticar e planejar",
    body: "Lista priorizada de problemas com evidência e um plano em 5 fases — ordenadas para que vitórias iniciais destravem o que vem depois.",
  },
  {
    num: "04",
    icon: FileStack,
    title: "Gerar relatórios",
    body: "Monta Markdown: visão geral do repositório, revisão de arquitetura, dívida técnica e plano de ação. Tudo revisável e baixável.",
  },
];

export function HowItWorks() {
  return (
    <section id="como-funciona" className="mt-24">
      <div className="mb-8">
        <div className="section-title">O pipeline</div>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-100 sm:text-3xl">
          Do repositório ao relatório — em uma única passagem.
        </h2>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STEPS.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.num} className="panel p-5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] tracking-widest text-violet-300">
                  {s.num}
                </span>
                <Icon size={18} className="text-zinc-500" />
              </div>
              <h3 className="mt-4 text-sm font-semibold text-zinc-100">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{s.body}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
