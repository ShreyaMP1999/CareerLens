from app.agents.workflow import AgentState, run_job_search_agent


def test_agent_workflow_ranks_and_drafts():
    result = run_job_search_agent(
        AgentState(
            request="Find Python Backend or AI Engineer jobs posted within the last 3 days",
            resume_text=(
                "Built Python FastAPI services with PostgreSQL, Docker, pytest, LangGraph, MCP, "
                "ChromaDB, RAG, and semantic search."
            ),
            min_match_score=50,
        )
    )
    assert result["status"] == "completed"
    assert result["qualified_jobs"]
    assert result["drafts"]
