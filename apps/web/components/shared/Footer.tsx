import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="mt-24 border-t border-bg-border bg-bg-base/60">
      <div className="mx-auto flex max-w-7xl flex-col items-start gap-3 px-6 py-8 text-xs text-zinc-500 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <Logo size={20} />
          <span className="text-zinc-300">ForgeOps</span>
          <span>— auditoria técnica de repositórios, pontuada e explicada.</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Licença MIT · 100% local · Sem telemetria</span>
        </div>
      </div>
    </footer>
  );
}
