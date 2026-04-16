import { notFound } from "next/navigation";
import { fetchAnalysis } from "@/lib/api";
import { AnalysisView } from "@/components/analysis/AnalysisView";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

type PageProps = {
  params: { id: string };
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  try {
    const session = await fetchAnalysis(params.id);
    return {
      title: `${session.repo_name} · ForgeOps`,
      description:
        session.summary?.headline ?? "Relatório de análise do ForgeOps.",
    };
  } catch {
    return { title: "Análise · ForgeOps" };
  }
}

export default async function AnalysisPage({ params }: PageProps) {
  let session;
  try {
    session = await fetchAnalysis(params.id);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return (
      <div className="panel mt-6 p-8 text-center">
        <h2 className="text-lg font-semibold text-rose-300">
          Não foi possível carregar esta análise.
        </h2>
        <p className="mt-2 text-sm text-zinc-400">{msg}</p>
        <a href="/" className="btn-primary mt-6 inline-flex">
          Iniciar uma nova análise
        </a>
      </div>
    );
  }
  if (!session) notFound();
  return <AnalysisView session={session} />;
}
