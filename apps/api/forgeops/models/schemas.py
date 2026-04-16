"""Pydantic models for the ForgeOps analysis domain."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high", "critical"]


class SourceType(str, Enum):
    upload = "upload"
    demo = "demo"


class AnalysisStatus(str, Enum):
    pending = "pending"
    running = "running"
    complete = "complete"
    failed = "failed"


class LanguageBreakdown(BaseModel):
    language: str
    files: int
    bytes: int
    share: float = Field(ge=0.0, le=1.0, description="Share of code bytes")


class FileTypeBreakdown(BaseModel):
    extension: str
    files: int
    bytes: int


class LargestFile(BaseModel):
    path: str
    bytes: int


class RepositoryStats(BaseModel):
    total_files: int
    total_directories: int
    total_size_bytes: int
    code_files: int
    code_size_bytes: int
    max_depth: int
    avg_depth: float
    file_type_breakdown: list[FileTypeBreakdown]
    language_breakdown: list[LanguageBreakdown]
    largest_files: list[LargestFile]
    config_files: list[str]
    docs_files: list[str]
    test_files: list[str]
    ci_files: list[str]
    container_files: list[str]
    env_files: list[str]
    dependency_files: list[str]
    suspicious_files: list[str]
    large_files_count: int
    binary_files_count: int


class DetectedStack(BaseModel):
    primary_languages: list[str]
    probable_frontend: list[str]
    probable_backend: list[str]
    package_managers: list[str]
    frameworks: list[str]
    databases: list[str]
    testing_tools: list[str]
    ci_tools: list[str]
    containerization: list[str]
    inferred_project_type: str


class ScoreDimension(BaseModel):
    key: str
    name: str
    score: int = Field(ge=0, le=100)
    weight: float = Field(ge=0.0, le=1.0)
    rationale: str
    positives: list[str]
    concerns: list[str]
    recommendations: list[str]


class IssueItem(BaseModel):
    id: str
    severity: Severity
    category: str
    title: str
    description: str
    evidence: list[str]
    recommendation: str


class RecommendationItem(BaseModel):
    id: str
    priority: Literal["now", "next", "later"]
    title: str
    rationale: str
    impact: Literal["low", "medium", "high"]
    effort: Literal["small", "medium", "large"]


class PlanTask(BaseModel):
    title: str
    detail: str
    effort: Literal["S", "M", "L"]


class PlanPhase(BaseModel):
    phase: int
    title: str
    goal: str
    impact: Literal["low", "medium", "high"]
    effort: Literal["small", "medium", "large"]
    risk: Literal["low", "medium", "high"]
    tasks: list[PlanTask]


class GeneratedDocument(BaseModel):
    slug: str
    title: str
    content: str


class AnalysisSummary(BaseModel):
    headline: str
    overall_score: int = Field(ge=0, le=100)
    grade: Literal["A+", "A", "B", "C", "D", "F"]
    risk_level: Literal["low", "medium", "high"]
    strengths: list[str]
    weaknesses: list[str]


class AnalysisSession(BaseModel):
    id: str
    source_type: SourceType
    repo_name: str
    created_at: datetime
    status: AnalysisStatus
    error: Optional[str] = None
    summary: Optional[AnalysisSummary] = None
    repository_stats: Optional[RepositoryStats] = None
    detected_stack: Optional[DetectedStack] = None
    scores: list[ScoreDimension] = Field(default_factory=list)
    issues: list[IssueItem] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    phases: list[PlanPhase] = Field(default_factory=list)
    generated_documents: list[GeneratedDocument] = Field(default_factory=list)

    model_config = {"json_schema_extra": {"example": {}}}
