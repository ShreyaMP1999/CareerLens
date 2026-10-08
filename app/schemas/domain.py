from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class WorkArrangement(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class ApplicationStatus(StrEnum):
    DISCOVERED = "Discovered"
    SAVED = "Saved"
    APPLIED = "Applied"
    RECRUITER_SCREEN = "Recruiter Screen"
    TECHNICAL_INTERVIEW = "Technical Interview"
    HIRING_MANAGER_INTERVIEW = "Hiring Manager Interview"
    FINAL_INTERVIEW = "Final Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


@dataclass
class ResumeProfile:
    raw_text: str
    skills: list[str]
    experience: list[str]
    education: list[str]
    projects: list[str]
    technologies: list[str]
    chunks: list[str] = field(default_factory=list)


@dataclass
class JobRequirements:
    title: str
    description: str
    required_skills: list[str]
    preferred_skills: list[str]
    years_experience: int | None = None
    education: list[str] = field(default_factory=list)
    seniority: str = "unknown"


@dataclass
class MatchReport:
    overall_score: float
    required_skills_matched: list[str]
    required_skills_missing: list[str]
    preferred_skills_matched: list[str]
    relevant_experience: list[str]
    missing_or_uncertain: list[str]
    suggestions: list[str]
    score_explanation: str
    evidence: list[str]
    weights: dict[str, float]


@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    provider_id: str | None = None
    posted_at: datetime | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    work_arrangement: WorkArrangement = WorkArrangement.UNKNOWN
    employment_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RankedJob:
    posting: JobPosting
    match_score: float
    matching_skills: list[str]
    missing_requirements: list[str]
    experience_requirement: int | None
    reason: str


@dataclass
class ApplicationRecord:
    company: str
    job_title: str
    job_url: str
    source: str
    location: str = ""
    work_arrangement: WorkArrangement = WorkArrangement.UNKNOWN
    salary_range: str | None = None
    posting_date: datetime | None = None
    application_date: datetime | None = None
    resume_match_score: float | None = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    recruiter_details: str | None = None
    notes: str = ""
    follow_up_date: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
