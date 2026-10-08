import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.mcp_server import tools


def main() -> None:
    resume = (
        "Built Python FastAPI services with PostgreSQL, Docker, pytest, MCP, RAG, and ChromaDB."
    )
    jd = "Requires Python, FastAPI, PostgreSQL, Docker, MCP, RAG, and ChromaDB."
    print(tools.match_resume(resume, jd))
    print(tools.search_fresh_jobs(query="Python Backend Engineer"))


if __name__ == "__main__":
    main()
