from __future__ import annotations

from app.mcp_server import tools


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Install the official MCP Python SDK to run the MCP server.") from exc

    mcp = FastMCP("CareerLens")

    mcp.tool(
        name="parse_resume",
        description="Parse resume text into skills, experience, education, projects, and chunks.",
    )(tools.parse_resume)
    mcp.tool(
        name="analyze_job_description",
        description="Extract required and preferred skills from a job description.",
    )(tools.analyze_job)
    mcp.tool(
        name="match_resume_to_job",
        description="Create an explainable evidence-based resume match report.",
    )(tools.match_resume)
    mcp.tool(name="identify_skill_gaps", description="List missing required and preferred skills.")(
        tools.skill_gaps
    )
    mcp.tool(
        name="suggest_resume_improvements",
        description="Suggest grounded resume improvements without inventing experience.",
    )(tools.suggest_improvements)
    mcp.tool(
        name="draft_recruiter_email",
        description="Draft grounded recruiter outreach using resume evidence.",
    )(tools.draft_email)
    mcp.tool(
        name="generate_email_variations",
        description="Generate alternate outreach drafts from a base email.",
    )(tools.email_variations)
    mcp.tool(
        name="draft_followup_email",
        description="Generate a follow-up variation from base evidence.",
    )(tools.email_variations)
    mcp.tool(
        name="validate_email_claims", description="Flag unverified claims in an outreach draft."
    )(tools.validate_email_claims)
    mcp.tool(
        name="create_gmail_draft",
        description="Create a Gmail draft only after explicit authorization and OAuth setup.",
    )(tools.gmail_draft)
    mcp.tool(name="save_job", description="Save a job to the application tracker.")(tools.save_job)
    mcp.tool(name="track_application", description="Alias for saving a tracked application.")(
        tools.save_job
    )
    mcp.tool(
        name="update_application_status",
        description="Update an application status and append history.",
    )(tools.update_application_status)
    mcp.tool(name="get_application_pipeline", description="Return tracked applications.")(
        tools.pipeline
    )
    mcp.tool(
        name="get_due_followups", description="Return applications whose follow-up date is due."
    )(lambda: {"followups": []})
    mcp.tool(
        name="get_application_analytics",
        description="Return application metrics with clear definitions.",
    )(tools.analytics)
    mcp.tool(
        name="search_fresh_jobs",
        description="Search fresh jobs; demo mode returns labeled sample data.",
    )(tools.search_fresh_jobs)
    mcp.tool(
        name="filter_jobs", description="Filter demo jobs by query, age, location, and experience."
    )(tools.search_fresh_jobs)
    mcp.tool(name="rank_jobs_by_resume", description="Rank jobs using resume match scoring.")(
        tools.rank_jobs
    )
    mcp.tool(name="get_job_details", description="Return demo job details for a provider id.")(
        lambda provider_id: {
            "provider_id": provider_id,
            "jobs": [tools.asdict(job) for job in tools.demo_job_postings()],
        }
    )
    mcp.tool(
        name="save_matched_jobs",
        description="Rank and return jobs that can be saved after user confirmation.",
    )(tools.rank_jobs)
    mcp.tool(name="find_duplicate_jobs", description="Find duplicate job postings.")(
        tools.duplicate_jobs
    )
    return mcp


def main() -> None:  # pragma: no cover
    mcp = build_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
