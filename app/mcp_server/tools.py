from __future__ import annotations

from dataclasses import asdict

from app.providers.demo_jobs import demo_job_postings
from app.schemas.domain import ApplicationRecord, ApplicationStatus
from app.services.email_drafter import (
    create_gmail_draft,
    draft_recruiter_email,
    generate_email_variations,
    validate_email_claims,
)
from app.services.job_analysis import analyze_job_description
from app.services.job_search import (
    JobSearchFilters,
    deduplicate_jobs,
    filter_jobs,
    find_duplicate_jobs,
    rank_jobs_by_resume,
)
from app.services.resume_parser import parse_resume_text
from app.services.scoring import identify_skill_gaps, match_resume_to_job
from app.services.tracker import ApplicationTracker

tracker = ApplicationTracker()


def parse_resume(resume_text: str) -> dict:
    return asdict(parse_resume_text(resume_text))


def analyze_job(job_description: str, title: str = "Role") -> dict:
    return asdict(analyze_job_description(job_description, title))


def match_resume(resume_text: str, job_description: str, title: str = "Role") -> dict:
    resume = parse_resume_text(resume_text)
    job = analyze_job_description(job_description, title)
    return asdict(match_resume_to_job(resume, job))


def skill_gaps(resume_text: str, job_description: str, title: str = "Role") -> dict:
    resume = parse_resume_text(resume_text)
    job = analyze_job_description(job_description, title)
    return {"gaps": identify_skill_gaps(resume, job)}


def suggest_improvements(resume_text: str, job_description: str, title: str = "Role") -> dict:
    return {"suggestions": match_resume(resume_text, job_description, title)["suggestions"]}


def search_fresh_jobs(
    query: str = "Python Backend Engineer",
    location: str = "",
    max_age_days: int = 14,
    max_experience_years: int | None = None,
) -> dict:
    jobs = demo_job_postings()
    filters = JobSearchFilters(
        title=query,
        location=location,
        max_age_days=max_age_days,
        max_experience_years=max_experience_years,
    )
    return {"mode": "demo", "jobs": [asdict(job) for job in filter_jobs(jobs, filters)]}


def rank_jobs(resume_text: str, query: str = "Python Backend Engineer") -> dict:
    resume = parse_resume_text(resume_text)
    jobs = filter_jobs(demo_job_postings(), JobSearchFilters(title=query, max_age_days=14))
    return {"ranked_jobs": [asdict(item) for item in rank_jobs_by_resume(resume, jobs)]}


def save_job(company: str, job_title: str, job_url: str, source: str = "manual") -> dict:
    return asdict(
        tracker.save_job(
            ApplicationRecord(company=company, job_title=job_title, job_url=job_url, source=source)
        )
    )


def update_application_status(application_id: str, status: str, note: str = "") -> dict:
    return asdict(tracker.update_status(str(application_id), ApplicationStatus(status), note))


def pipeline() -> dict:
    return {"applications": [asdict(record) for record in tracker.records.values()]}


def analytics() -> dict:
    return tracker.analytics()


def draft_email(
    resume_text: str,
    job_description: str,
    job_title: str,
    company_name: str,
    recruiter_name: str | None = None,
) -> dict:
    resume = parse_resume_text(resume_text)
    job = analyze_job_description(job_description, job_title)
    return asdict(draft_recruiter_email(resume, job, company_name, recruiter_name))


def email_variations(base_body: str, evidence: list[str] | None = None) -> dict:
    from app.services.email_drafter import EmailDraft

    base = EmailDraft(
        "Recruiter outreach",
        base_body,
        evidence or [],
        validate_email_claims(base_body, evidence or []),
    )
    return {"variations": [asdict(item) for item in generate_email_variations(base)]}


def duplicate_jobs() -> dict:
    jobs = demo_job_postings() + [demo_job_postings()[0]]
    return {
        "duplicates": [[asdict(item) for item in group] for group in find_duplicate_jobs(jobs)],
        "deduplicated_count": len(deduplicate_jobs(jobs)),
    }


def gmail_draft(authorized: bool = False) -> dict:
    return create_gmail_draft(authorized=authorized)
