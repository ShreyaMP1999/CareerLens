from datetime import UTC, datetime

from app.schemas.domain import ApplicationRecord, ApplicationStatus
from app.services.email_drafter import create_gmail_draft, draft_recruiter_email
from app.services.job_analysis import analyze_job_description
from app.services.resume_parser import parse_resume_text
from app.services.tracker import ApplicationTracker


def test_email_draft_is_grounded_and_gmail_requires_authorization():
    resume = parse_resume_text(
        "Built Python FastAPI services with PostgreSQL, Docker, pytest, and RAG."
    )
    job = analyze_job_description(
        "Requires Python, FastAPI, PostgreSQL, and Docker.", "Backend Engineer"
    )
    draft = draft_recruiter_email(resume, job, "Acme AI", recruiter_name="Sam")
    assert "Acme AI" in draft.subject
    assert draft.evidence_used
    assert draft.unverified_claims == []
    assert create_gmail_draft(authorized=False)["status"] == "approval_required"


def test_application_tracker_crud_analytics_and_followups():
    tracker = ApplicationTracker()
    record = tracker.save_job(
        ApplicationRecord(
            company="Acme AI",
            job_title="Backend Engineer",
            job_url="https://example.com/job/1",
            source="demo",
            follow_up_date=datetime.now(UTC),
        )
    )
    duplicate = tracker.save_job(
        ApplicationRecord(
            company="Acme AI",
            job_title="Backend Engineer",
            job_url="https://www.example.com/job/1",
            source="demo",
        )
    )
    assert duplicate.id == record.id
    tracker.update_status(str(record.id), ApplicationStatus.APPLIED)
    analytics = tracker.analytics()
    assert analytics["total_jobs_discovered"] == 1
    assert analytics["total_applications_submitted"] == 1
    assert tracker.get_due_followups()
