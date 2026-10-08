import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.workflow import AgentState, run_job_search_agent

if __name__ == "__main__":
    resume = (
        "Built Python FastAPI services with PostgreSQL, Docker, pytest, HTTPX, asyncio, "
        "LangGraph, MCP, ChromaDB, RAG, and semantic search."
    )
    print(
        run_job_search_agent(
            AgentState(
                request="Find Python Backend or AI Engineer jobs posted within the last 3 days",
                resume_text=resume,
                min_match_score=50,
            )
        )
    )
