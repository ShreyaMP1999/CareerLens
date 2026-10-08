# Technical Overview

CareerLens is organized around shared services. FastAPI, Streamlit, MCP tools, and the agent workflow call the same service layer so behavior remains consistent across interfaces.

## Data Flow

1. Resume text is extracted from PDF, DOCX, TXT, or Markdown.
2. The parser extracts skills, evidence snippets, education markers, projects, and text chunks.
3. RAG indexing stores chunks per user. The included local fallback is deterministic for tests; production can replace it with ChromaDB plus sentence-transformers.
4. Job descriptions are analyzed for required skills, preferred skills, education, seniority, and years of experience.
5. Matching uses a transparent weighted function. LLMs may help interpret evidence, but the final score is deterministic and explainable.
6. Outreach drafts are generated only from retrieved resume evidence and flagged for unverified claims.
7. Application tracking stores records, statuses, history, follow-up dates, and analytics.

## MCP Notes

The implementation follows the current official MCP Python SDK direction: `FastMCP` plus stdio for local clients and Streamable HTTP support when running an ASGI app. Older SSE-only examples are intentionally not the main path.

## Security Notes

Resume files and job descriptions are untrusted input. API keys are environment variables only. Gmail draft creation returns `approval_required` unless the caller explicitly authorizes the side effect and configures OAuth.

