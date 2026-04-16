import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Nav } from "@/components/shared/Nav";
import { Footer } from "@/components/shared/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ForgeOps — Auditoria técnica de repositórios",
  description:
    "Envie um repositório e receba um relatório de saúde técnica: notas, problemas com evidências, plano em fases e documentação gerada em Markdown.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="min-h-screen bg-bg-base font-sans text-zinc-100 antialiased">
        <Nav />
        <main className="mx-auto max-w-7xl px-6 pb-28 pt-10 sm:pt-14">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
