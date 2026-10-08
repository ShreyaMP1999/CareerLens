from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.core.config import get_settings
from app.providers.demo_jobs import demo_job_postings
from app.schemas.domain import ApplicationRecord
from app.services.email_drafter import draft_recruiter_email
from app.services.job_analysis import analyze_job_description
from app.services.job_search import JobSearchFilters, filter_jobs, rank_jobs_by_resume
from app.services.resume_parser import extract_text_from_file, parse_resume_text
from app.services.scoring import identify_skill_gaps, match_resume_to_job
from app.services.tracker import ApplicationTracker

tracker = ApplicationTracker()


def create_app():
    try:
        from fastapi import FastAPI, File, HTTPException, UploadFile
        from pydantic import BaseModel
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Install FastAPI dependencies to run the API.") from exc

    app = FastAPI(title="JobPilot AI", version="0.1.0")

    class MatchRequest(BaseModel):
        resume_text: str
        job_description: str
        job_title: str = "Role"

    class JobSearchRequest(BaseModel):
        resume_text: str
        query: str = "python backend engineer"
        location: str = ""
        max_age_days: int | None = 14
        max_experience_years: int | None = None
        min_match_score: float | None = None

    class OutreachRequest(BaseModel):
        resume_text: str
        job_description: str
        job_title: str
        company_name: str
        recruiter_name: str | None = None
        tone: str = "warm and concise"

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "demo" if get_settings().demo_mode else "live"}

    @app.post("/resumes/parse")
    async def parse_resume(file: UploadFile = File(...)):
        suffix = Path(file.filename or "resume.txt").suffix
        with NamedTemporaryFile(suffix=suffix) as handle:
            handle.write(await file.read())
            handle.flush()
            text = extract_text_from_file(handle.name, max_mb=get_settings().max_upload_mb)
        return asdict(parse_resume_text(text))

    @app.post("/match")
    def match(request: MatchRequest):
        resume = parse_resume_text(request.resume_text)
        job = analyze_job_description(request.job_description, request.job_title)
        return asdict(match_resume_to_job(resume, job))

    @app.post("/skill-gaps")
    def skill_gaps(request: MatchRequest):
        resume = parse_resume_text(request.resume_text)
        job = analyze_job_description(request.job_description, request.job_title)
        return {"gaps": identify_skill_gaps(resume, job)}

    @app.post("/jobs/search")
    def search_jobs(request: JobSearchRequest):
        resume = parse_resume_text(request.resume_text)
        filters = JobSearchFilters(
            title=request.query,
            location=request.location,
            max_age_days=request.max_age_days,
            max_experience_years=request.max_experience_years,
            min_match_score=request.min_match_score,
        )
        jobs = filter_jobs(demo_job_postings(), filters)
        ranked = rank_jobs_by_resume(resume, jobs)
        if request.min_match_score is not None:
            ranked = [job for job in ranked if job.match_score >= request.min_match_score]
        return [asdict(item) for item in ranked]

    @app.post("/outreach/draft")
    def outreach(request: OutreachRequest):
        resume = parse_resume_text(request.resume_text)
        job = analyze_job_description(request.job_description, request.job_title)
        return asdict(
            draft_recruiter_email(
                resume=resume,
                job=job,
                company_name=request.company_name,
                recruiter_name=request.recruiter_name,
                tone=request.tone,
            )
        )

    @app.post("/applications")
    def save_application(record: dict):
        try:
            saved = tracker.save_job(ApplicationRecord(**record))
        except TypeError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return asdict(saved)

    @app.get("/applications/analytics")
    def analytics():
        return tracker.analytics()

    return app


app = create_app()


def run() -> None:  # pragma: no cover
    import uvicorn

    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)

