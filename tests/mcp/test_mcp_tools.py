from app.mcp_server import tools


def test_mcp_tool_functions_execute():
    resume = "Built Python FastAPI services with PostgreSQL, Docker, pytest, LangGraph, MCP, RAG, and ChromaDB."
    jd = "Requires Python, FastAPI, PostgreSQL, Docker, LangGraph, and ChromaDB."
    parsed = tools.parse_resume(resume)
    assert "python" in parsed["skills"]
    match = tools.match_resume(resume, jd)
    assert match["overall_score"] > 50
    search = tools.search_fresh_jobs(query="AI Backend Engineer", max_age_days=3)
    assert search["mode"] == "demo"
    saved = tools.save_job("Acme AI", "AI Backend Engineer", "https://example.com/acme-ai")
    updated = tools.update_application_status(saved["id"], "Applied")
    assert updated["status"] == "Applied"
