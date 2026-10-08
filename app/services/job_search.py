from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.schemas.domain import JobPosting, RankedJob, ResumeProfile, WorkArrangement
from app.services.job_analysis import analyze_job_description
from app.services.scoring import match_resume_to_job
from app.services.skills import extract_years_experience


@dataclass
class JobSearchFilters:
    title: str = ""
    keywords: list[str] | None = None
    location: str = ""
    arrangement: WorkArrangement | None = None
    max_experience_years: int | None = None
    min_salary: int | None = None
    max_salary: int | None = None
    max_age_days: int | None = 14
    company: str | None = None
    min_match_score: float | None = None


def normalize_job_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


def find_duplicate_jobs(jobs: list[JobPosting]) -> list[list[JobPosting]]:
    groups: dict[str, list[JobPosting]] = {}
    for job in jobs:
        key = job.provider_id or normalize_job_url(job.url) or f"{job.company}:{job.title}:{job.location}"
        groups.setdefault(key.lower(), []).append(job)
    return [group for group in groups.values() if len(group) > 1]


def deduplicate_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    seen: set[str] = set()
    unique: list[JobPosting] = []
    for job in jobs:
        key = (job.provider_id or normalize_job_url(job.url) or f"{job.company}:{job.title}").lower()
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


def filter_jobs(
    jobs: list[JobPosting],
    filters: JobSearchFilters,
    now: datetime | None = None,
) -> list[JobPosting]:
    current = now or datetime.now(timezone.utc)
    filtered: list[JobPosting] = []
    keywords = [word.lower() for word in (filters.keywords or [])]
    for job in jobs:
        haystack = f"{job.title} {job.company} {job.description} {job.location}".lower()
        if filters.title and filters.title.lower() not in haystack:
            continue
        if keywords and not all(keyword in haystack for keyword in keywords):
            continue
        if filters.location and filters.location.lower() not in job.location.lower():
            continue
        if filters.company and filters.company.lower() not in job.company.lower():
            continue
        if filters.arrangement and job.work_arrangement != filters.arrangement:
            continue
        if filters.min_salary and job.salary_max and job.salary_max < filters.min_salary:
            continue
        if filters.max_salary and job.salary_min and job.salary_min > filters.max_salary:
            continue
        if filters.max_age_days is not None:
            if not job.posted_at:
                continue
            age_days = (current - job.posted_at).days
            if age_days > filters.max_age_days:
                continue
        if filters.max_experience_years is not None:
            years = extract_years_experience(job.description)
            if years is not None and years > filters.max_experience_years:
                continue
        filtered.append(job)
    return filtered


def rank_jobs_by_resume(resume: ResumeProfile, jobs: list[JobPosting]) -> list[RankedJob]:
    ranked: list[RankedJob] = []
    for posting in jobs:
        requirements = analyze_job_description(posting.description, posting.title)
        report = match_resume_to_job(resume, requirements)
        ranked.append(
            RankedJob(
                posting=posting,
                match_score=report.overall_score,
                matching_skills=report.required_skills_matched + report.preferred_skills_matched,
                missing_requirements=report.required_skills_missing,
                experience_requirement=requirements.years_experience,
                reason=report.score_explanation,
            )
        )
    ranked.sort(key=lambda item: item.match_score, reverse=True)
    return ranked

