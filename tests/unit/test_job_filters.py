from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.providers.demo_jobs import demo_job_postings
from app.services.job_search import (
    JobSearchFilters,
    deduplicate_jobs,
    filter_jobs,
    find_duplicate_jobs,
    normalize_job_url,
)


def test_freshness_and_experience_filters():
    now = datetime.now(UTC)
    jobs = demo_job_postings(now)
    filtered = filter_jobs(
        jobs,
        JobSearchFilters(max_age_days=3, max_experience_years=4),
        now=now,
    )
    assert all(job.posted_at and (now - job.posted_at).days <= 3 for job in filtered)
    assert all("7 years" not in job.description.lower() for job in filtered)


def test_salary_filter_and_duplicate_detection():
    jobs = demo_job_postings(datetime.now(UTC))
    jobs[0].posted_at = datetime.now(UTC) - timedelta(days=1)
    filtered = filter_jobs(jobs, JobSearchFilters(min_salary=130000, max_age_days=14))
    assert filtered
    duplicated = jobs + [jobs[0]]
    assert find_duplicate_jobs(duplicated)
    assert len(deduplicate_jobs(duplicated)) == len(jobs)
    assert normalize_job_url("https://www.example.com/jobs/123?x=1") == "example.com/jobs/123"


@pytest.mark.parametrize(
    ("first_changes", "second_changes", "is_duplicate"),
    [
        (
            {"source": "provider-a", "provider_id": "123"},
            {"source": "provider-b", "provider_id": "123"},
            False,
        ),
        (
            {"source": "provider-a", "provider_id": "123"},
            {"source": "provider-a", "provider_id": "123", "url": "https://other.com/123"},
            True,
        ),
        (
            {"source": "provider-a", "provider_id": "ABC"},
            {"source": "provider-a", "provider_id": "abc"},
            False,
        ),
        (
            {"provider_id": None, "url": "https://www.example.com/jobs/123?ref=a"},
            {"provider_id": None, "url": "https://example.com/jobs/123/"},
            True,
        ),
        (
            {"provider_id": None, "url": "https://example.com/jobs/ABC"},
            {"provider_id": None, "url": "https://example.com/jobs/abc"},
            False,
        ),
        (
            {"provider_id": None, "url": "", "location": "Seattle"},
            {"provider_id": None, "url": "", "location": "Boston"},
            False,
        ),
        (
            {"provider_id": None, "url": "", "location": "Seattle"},
            {"provider_id": None, "url": "", "location": " seattle "},
            True,
        ),
    ],
)
def test_duplicate_detection_and_removal_use_consistent_job_identity(
    first_changes, second_changes, is_duplicate
):
    original = demo_job_postings(datetime.now(UTC))[0]
    first = replace(original, **first_changes)
    second = replace(original, **second_changes)
    jobs = [first, second]
    assert find_duplicate_jobs(jobs) == ([jobs] if is_duplicate else [])
    assert deduplicate_jobs(jobs) == ([first] if is_duplicate else jobs)
