from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.providers.demo_jobs import demo_job_postings
from app.schemas.domain import RankedJob
from app.services.email_drafter import EmailDraft, draft_recruiter_email
from app.services.job_analysis import analyze_job_description
from app.services.job_search import JobSearchFilters, filter_jobs, rank_jobs_by_resume
from app.services.resume_parser import parse_resume_text


@dataclass
class AgentState:
    request: str
    resume_text: str
    max_age_days: int = 3
    min_match_score: float = 85
    query: str = "Python Backend Engineer"
    errors: list[str] = field(default_factory=list)
    ranked_jobs: list[RankedJob] = field(default_factory=list)
    drafts: list[EmailDraft] = field(default_factory=list)


def run_job_search_agent(state: AgentState) -> dict:
    """Bounded deterministic workflow mirroring the LangGraph production shape."""
    if "ai engineer" in state.request.lower():
        state.query = "AI Backend Engineer"
    resume = parse_resume_text(state.resume_text)
    filters = JobSearchFilters(
        title=state.query, max_age_days=state.max_age_days, max_experience_years=4
    )
    jobs = filter_jobs(demo_job_postings(), filters)
    state.ranked_jobs = [
        item
        for item in rank_jobs_by_resume(resume, jobs)
        if item.match_score >= state.min_match_score
    ][:3]
    for ranked in state.ranked_jobs:
        job_requirements = analyze_job_description(ranked.posting.description, ranked.posting.title)
        state.drafts.append(
            draft_recruiter_email(
                resume=resume,
                job=job_requirements,
                company_name=ranked.posting.company,
                recruiter_name=None,
            )
        )
    return {
        "status": "completed",
        "qualified_jobs": [asdict(item) for item in state.ranked_jobs],
        "drafts": [asdict(item) for item in state.drafts],
        "notes": "Demo mode uses labeled sample jobs. Live mode requires Adzuna credentials.",
    }


def demo_main() -> None:  # pragma: no cover
    sample_resume = (
        "Built Python FastAPI services with PostgreSQL, Docker, pytest, LangGraph, MCP tool "
        "calling, ChromaDB, RAG, and semantic search."
    )
    result = run_job_search_agent(
        AgentState(
            request="Find Python Backend or AI Engineer jobs posted within the last 3 days",
            resume_text=sample_resume,
        )
    )
    print(result)
