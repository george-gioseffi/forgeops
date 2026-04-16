import type { AnalysisSession, GeneratedDocument, RecentAnalysis } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      if (data?.detail) detail = data.detail;
    } catch {
      // Ignore non-JSON errors
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
  return handleResponse(res);
}

export async function analyzeDemo(): Promise<AnalysisSession> {
  const res = await fetch(`${API_BASE_URL}/api/analyze/demo`, {
    method: "POST",
    cache: "no-store",
  });
  return handleResponse<AnalysisSession>(res);
}

export async function analyzeUpload(file: File): Promise<AnalysisSession> {
  const body = new FormData();
  body.append("file", file);
  const res = await fetch(`${API_BASE_URL}/api/analyze/upload`, {
    method: "POST",
    body,
  });
  return handleResponse<AnalysisSession>(res);
}

export async function fetchAnalysis(id: string): Promise<AnalysisSession> {
  const res = await fetch(`${API_BASE_URL}/api/analysis/${id}`, {
    cache: "no-store",
  });
  return handleResponse<AnalysisSession>(res);
}

export async function fetchDocuments(
  id: string
): Promise<{ id: string; repo_name: string; documents: GeneratedDocument[] }> {
  const res = await fetch(`${API_BASE_URL}/api/analysis/${id}/documents`, {
    cache: "no-store",
  });
  return handleResponse(res);
}

export async function fetchRecentAnalyses(): Promise<RecentAnalysis[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/analysis`, {
      cache: "no-store",
    });
    const data = await handleResponse<{ items: RecentAnalysis[] }>(res);
    return data.items ?? [];
  } catch {
    return [];
  }
}
