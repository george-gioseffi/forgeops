import Link from "next/link";

export default function NotFound() {
  return (
    <div className="panel mx-auto mt-16 max-w-xl p-8 text-center">
      <h2 className="text-xl font-semibold text-zinc-100">Análise não encontrada</h2>
      <p className="mt-2 text-sm text-zinc-400">
        O identificador informado não existe ou foi removido.
      </p>
      <Link href="/" className="btn-primary mt-6 inline-flex">
        Iniciar uma nova análise
      </Link>
    </div>
  );
}
