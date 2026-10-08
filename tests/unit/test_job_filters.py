from datetime import datetime, timedelta, timezone

from app.providers.demo_jobs import demo_job_postings
from app.services.job_search import (
    JobSearchFilters,
    deduplicate_jobs,
    filter_jobs,
    find_duplicate_jobs,
    normalize_job_url,
)


def test_freshness_and_experience_filters():
    now = datetime.now(timezone.utc)
    jobs = demo_job_postings(now)
    filtered = filter_jobs(
        jobs,
        JobSearchFilters(max_age_days=3, max_experience_years=4),
        now=now,
    )
    assert all(job.posted_at and (now - job.posted_at).days <= 3 for job in filtered)
    assert all("7 years" not in job.description.lower() for job in filtered)


def test_salary_filter_and_duplicate_detection():
    jobs = demo_job_postings(datetime.now(timezone.utc))
    jobs[0].posted_at = datetime.now(timezone.utc) - timedelta(days=1)
    filtered = filter_jobs(jobs, JobSearchFilters(min_salary=130000, max_age_days=14))
    assert filtered
    duplicated = jobs + [jobs[0]]
    assert find_duplicate_jobs(duplicated)
    assert len(deduplicate_jobs(duplicated)) == len(jobs)
    assert normalize_job_url("https://www.example.com/jobs/123?x=1") == "example.com/jobs/123"

