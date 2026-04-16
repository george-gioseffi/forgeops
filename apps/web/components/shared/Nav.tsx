import Link from "next/link";
import { Github, Compass } from "lucide-react";
import { Logo } from "./Logo";

export function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-bg-border/80 bg-bg-base/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2.5">
          <Logo />
          <div className="leading-tight">
            <div className="text-base font-semibold tracking-tight text-zinc-100">
              ForgeOps
            </div>
            <div className="text-[11px] uppercase tracking-[0.22em] text-zinc-500">
              Auditoria de repositório
            </div>
          </div>
        </Link>
        <nav className="flex items-center gap-2">
          <Link href="/#como-funciona" className="btn-tab hidden sm:inline-flex">
            <Compass size={14} /> Como funciona
          </Link>
          <Link
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost !px-4 !py-2"
          >
            <Github size={16} />
            <span className="hidden sm:inline">GitHub</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}
