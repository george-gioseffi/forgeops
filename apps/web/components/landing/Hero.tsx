import { Sparkles, ShieldCheck, Gauge, FileText } from "lucide-react";

export function Hero() {
  return (
    <section className="hero-bg relative overflow-hidden rounded-3xl border border-bg-border bg-bg-raised/60 px-6 py-14 sm:px-12 sm:py-20">
      <div className="max-w-3xl">
        <span className="chip-accent">
          <Sparkles size={13} /> Workspace de auditoria de repositório
        </span>
        <h1 className="mt-5 text-4xl font-semibold leading-[1.08] tracking-tight text-zinc-50 sm:text-5xl">
          Analise um repositório
          <br />
          <span className="bg-gradient-to-r from-violet-200 via-violet-300 to-violet-500 bg-clip-text text-transparent">
            e receba um raio‑X técnico.
          </span>
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-zinc-400 sm:text-lg">
          Envie um ZIP ou rode a análise da demo. O ForgeOps varre a árvore de arquivos,
          pontua <strong className="text-zinc-200">7 dimensões de engenharia</strong>, aponta
          problemas com evidências e gera um plano em fases junto com documentação em Markdown —
          tudo local, sem chaves de API.
        </p>
        <div className="mt-8 flex flex-wrap items-center gap-3">
          <a href="#inicio" className="btn-primary">
            Analisar um repositório
          </a>
          <a href="#como-funciona" className="btn-ghost">
            Como funciona
          </a>
        </div>
      </div>

      <div className="relative mt-14 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { icon: Gauge, label: "7", sub: "Dimensões pontuadas" },
          { icon: ShieldCheck, label: "25+", sub: "Regras heurísticas" },
          { icon: FileText, label: "4", sub: "Relatórios gerados" },
          { icon: Sparkles, label: "Local", sub: "Zero chamadas externas" },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.sub}
              className="panel bg-bg-card/80 p-4 transition-colors hover:border-violet-500/30"
            >
              <div className="flex items-center gap-2.5">
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-violet-500/25 bg-violet-500/10 text-violet-200">
                  <Icon size={14} />
                </span>
                <div className="text-[10px] uppercase tracking-[0.18em] text-zinc-500">
                  {item.sub}
                </div>
              </div>
              <div className="mt-3 text-2xl font-semibold tracking-tight text-zinc-50">
                {item.label}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
