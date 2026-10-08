from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.schemas.domain import JobPosting, WorkArrangement


def demo_job_postings(now: datetime | None = None) -> list[JobPosting]:
    current = now or datetime.now(UTC)
    return [
        JobPosting(
            title="AI Backend Engineer",
            company="Northstar Health AI",
            location="Remote - US",
            work_arrangement=WorkArrangement.REMOTE,
            description=(
                "Build Python FastAPI services for RAG workflows with PostgreSQL, Docker, "
                "LangGraph, MCP tool calling, pytest, and semantic search. Requires 3 years "
                "experience. Preferred: ChromaDB and AWS."
            ),
            url="https://example.com/jobs/northstar-ai-backend",
            provider_id="demo-northstar-ai-backend",
            source="demo",
            posted_at=current - timedelta(days=1),
            salary_min=140000,
            salary_max=175000,
        ),
        JobPosting(
            title="Senior Platform Engineer",
            company="Orbit Systems",
            location="San Francisco, CA",
            work_arrangement=WorkArrangement.HYBRID,
            description=(
                "Senior engineer for Kubernetes microservices. Requires 7 years experience, "
                "Go, Terraform, AWS, and incident management. Python is a plus."
            ),
            url="https://example.com/jobs/orbit-platform",
            provider_id="demo-orbit-platform",
            source="demo",
            posted_at=current - timedelta(days=5),
            salary_min=170000,
            salary_max=210000,
        ),
        JobPosting(
            title="Python Backend Engineer",
            company="BrightHire Labs",
            location="New York, NY",
            work_arrangement=WorkArrangement.ONSITE,
            description=(
                "Develop REST API services with Python, FastAPI, SQLAlchemy, PostgreSQL, "
                "HTTPX, asyncio, Docker, and GitHub Actions. Requires 4 years experience."
            ),
            url="https://example.com/jobs/brighthire-python",
            provider_id="demo-brighthire-python",
            source="demo",
            posted_at=current - timedelta(days=3),
            salary_min=125000,
            salary_max=160000,
        ),
    ]
