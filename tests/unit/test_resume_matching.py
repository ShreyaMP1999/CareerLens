from app.services.job_analysis import analyze_job_description
from app.services.resume_parser import chunk_text, parse_resume_text
from app.services.scoring import identify_skill_gaps, match_resume_to_job


def test_resume_skill_extraction_and_chunking():
    resume = parse_resume_text(
        "Built Python FastAPI services with PostgreSQL, Docker, pytest, "
        "LangGraph, MCP, RAG, and ChromaDB."
    )
    assert "python" in resume.skills
    assert "fastapi" in resume.skills
    assert "postgresql" in resume.skills
    assert chunk_text("one two three four", chunk_size=2, overlap=1) == [
        "one two",
        "two three",
        "three four",
    ]


def test_job_requirement_extraction():
    job = analyze_job_description(
        "Requires Python, FastAPI, PostgreSQL, Docker, and 3 years experience. "
        "Preferred: ChromaDB.",
        "AI Backend Engineer",
    )
    assert "python" in job.required_skills
    assert "chromadb" in job.preferred_skills
    assert job.years_experience == 3


def test_explainable_match_score_and_skill_gaps():
    resume = parse_resume_text(
        "Built Python FastAPI APIs with PostgreSQL, Docker, pytest, and RAG."
    )
    job = analyze_job_description("Requires Python, FastAPI, LangGraph, ChromaDB, and Docker.")
    report = match_resume_to_job(resume, job)
    assert 0 <= report.overall_score <= 100
    assert "python" in report.required_skills_matched
    assert "chromadb" in report.required_skills_missing
    assert "chromadb" in identify_skill_gaps(resume, job)
