from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from app.agents.workflow import AgentState, run_job_search_agent
from app.providers.demo_jobs import demo_job_postings
from app.services.email_drafter import draft_recruiter_email
from app.services.job_analysis import analyze_job_description
from app.services.job_search import JobSearchFilters, filter_jobs, rank_jobs_by_resume
from app.services.resume_parser import parse_resume_text
from app.services.scoring import match_resume_to_job
from app.services.tracker import ApplicationTracker

st.set_page_config(page_title="CareerLens", layout="wide")

SAMPLE_RESUME = (
    "Built Python FastAPI APIs with SQLAlchemy, PostgreSQL, Docker, pytest, HTTPX, asyncio, "
    "LangGraph, MCP tool calling, ChromaDB, RAG, sentence transformers, and semantic search."
)

if "tracker" not in st.session_state:
    st.session_state.tracker = ApplicationTracker()

st.sidebar.title("CareerLens")
page = st.sidebar.radio(
    "Page",
    [
        "Dashboard",
        "Resume Matcher",
        "Fresh Job Finder",
        "AI Outreach",
        "Application Tracker",
        "Agent Demo",
    ],
)
st.sidebar.caption("Demo data is clearly labeled. Live Adzuna search needs API credentials.")

if page == "Dashboard":
    st.title("Dashboard")
    analytics = st.session_state.tracker.analytics()
    cols = st.columns(4)
    cols[0].metric("Jobs discovered", analytics["total_jobs_discovered"])
    cols[1].metric("Applications", analytics["total_applications_submitted"])
    cols[2].metric("Interviews", analytics["interviews_received"])
    cols[3].metric("Response rate", analytics["response_rate"])
    st.subheader("Recent demo jobs")
    st.dataframe([asdict(job) for job in demo_job_postings()], use_container_width=True)

elif page == "Resume Matcher":
    st.title("Resume Matcher")
    resume_text = st.text_area("Resume text", SAMPLE_RESUME, height=140)
    jd = st.text_area(
        "Job description",
        demo_job_postings()[0].description,
        height=180,
    )
    if st.button("Analyze match"):
        report = match_resume_to_job(
            parse_resume_text(resume_text), analyze_job_description(jd, "Role")
        )
        st.metric("Match score", report.overall_score)
        st.write(asdict(report))

elif page == "Fresh Job Finder":
    st.title("Fresh Job Finder")
    resume_text = st.text_area("Resume text", SAMPLE_RESUME, height=120)
    query = st.text_input("Role query", "AI Backend Engineer")
    max_age = st.slider("Maximum job age in days", 1, 14, 3)
    max_exp = st.slider("Maximum clearly stated years of experience", 0, 10, 4)
    if st.button("Search and rank"):
        jobs = filter_jobs(
            demo_job_postings(),
            JobSearchFilters(title=query, max_age_days=max_age, max_experience_years=max_exp),
        )
        ranked = rank_jobs_by_resume(parse_resume_text(resume_text), jobs)
        st.dataframe([asdict(job) for job in ranked], use_container_width=True)

elif page == "AI Outreach":
    st.title("AI Outreach")
    resume_text = st.text_area("Resume text", SAMPLE_RESUME, height=120)
    job = demo_job_postings()[0]
    company = st.text_input("Company", job.company)
    title = st.text_input("Job title", job.title)
    recruiter = st.text_input("Recruiter name", "")
    if st.button("Generate draft"):
        draft = draft_recruiter_email(
            parse_resume_text(resume_text),
            analyze_job_description(job.description, title),
            company,
            recruiter_name=recruiter or None,
        )
        st.text_input("Subject", draft.subject)
        st.text_area("Body", draft.body, height=260)
        st.write("Evidence used", draft.evidence_used)
        st.write("Unverified claims", draft.unverified_claims)

elif page == "Application Tracker":
    st.title("Application Tracker")
    st.write("Use the API or MCP tools to save jobs. This demo session stores records in memory.")
    st.write(st.session_state.tracker.analytics())

elif page == "Agent Demo":
    st.title("Agent Demo")
    request = st.text_input(
        "Natural-language workflow",
        "Find Python Backend or AI Engineer jobs posted within the last 3 days and draft outreach.",
    )
    resume_text = st.text_area("Resume text", SAMPLE_RESUME, height=140)
    if st.button("Run workflow"):
        result = run_job_search_agent(AgentState(request=request, resume_text=resume_text))
        st.write(result)
