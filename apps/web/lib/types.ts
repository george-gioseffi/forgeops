// Types mirror the Pydantic schemas from apps/api/forgeops/models/schemas.py.

export type Severity = "low" | "medium" | "high" | "critical";
export type Priority = "now" | "next" | "later";
export type Impact = "low" | "medium" | "high";
export type Effort = "small" | "medium" | "large";

export interface LanguageBreakdown {
  language: string;
  files: number;
  bytes: number;
  share: number;
}

export interface FileTypeBreakdown {
  extension: string;
  files: number;
  bytes: number;
}

export interface LargestFile {
  path: string;
  bytes: number;
}

export interface RepositoryStats {
  total_files: number;
  total_directories: number;
  total_size_bytes: number;
  code_files: number;
  code_size_bytes: number;
  max_depth: number;
  avg_depth: number;
  file_type_breakdown: FileTypeBreakdown[];
  language_breakdown: LanguageBreakdown[];
  largest_files: LargestFile[];
  config_files: string[];
  docs_files: string[];
  test_files: string[];
  ci_files: string[];
  container_files: string[];
  env_files: string[];
  dependency_files: string[];
  suspicious_files: string[];
  large_files_count: number;
  binary_files_count: number;
}

export interface DetectedStack {
  primary_languages: string[];
  probable_frontend: string[];
  probable_backend: string[];
  package_managers: string[];
  frameworks: string[];
  databases: string[];
  testing_tools: string[];
  ci_tools: string[];
  containerization: string[];
  inferred_project_type: string;
}

export interface ScoreDimension {
  key: string;
  name: string;
  score: number;
  weight: number;
  rationale: string;
  positives: string[];
  concerns: string[];
  recommendations: string[];
}

export interface IssueItem {
  id: string;
  severity: Severity;
  category: string;
  title: string;
  description: string;
  evidence: string[];
  recommendation: string;
}

export interface RecommendationItem {
  id: string;
  priority: Priority;
  title: string;
  rationale: string;
  impact: Impact;
  effort: Effort;
}

export interface PlanTask {
  title: string;
  detail: string;
  effort: "S" | "M" | "L";
}

export interface PlanPhase {
  phase: number;
  title: string;
  goal: string;
  impact: Impact;
  effort: Effort;
  risk: Impact;
  tasks: PlanTask[];
}

export interface GeneratedDocument {
  slug: string;
  title: string;
  content: string;
}

export interface AnalysisSummary {
  headline: string;
  overall_score: number;
  grade: "A+" | "A" | "B" | "C" | "D" | "F";
  risk_level: "low" | "medium" | "high";
  strengths: string[];
  weaknesses: string[];
}

export interface AnalysisSession {
  id: string;
  source_type: "upload" | "demo";
  repo_name: string;
  created_at: string;
  status: "pending" | "running" | "complete" | "failed";
  error?: string | null;
  summary?: AnalysisSummary | null;
  repository_stats?: RepositoryStats | null;
  detected_stack?: DetectedStack | null;
  scores: ScoreDimension[];
  issues: IssueItem[];
  recommendations: RecommendationItem[];
  phases: PlanPhase[];
  generated_documents: GeneratedDocument[];
}

export interface RecentAnalysis {
  id: string;
  repo_name: string;
  source_type: string;
  created_at: string;
  status: string;
  overall: number | null;
  grade: string | null;
}
