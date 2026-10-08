from __future__ import annotations

import re

CANONICAL_SKILLS = [
    "python",
    "fastapi",
    "pydantic",
    "sqlalchemy",
    "postgresql",
    "docker",
    "pytest",
    "aws",
    "gcp",
    "azure",
    "langgraph",
    "langchain",
    "model context protocol",
    "mcp",
    "rag",
    "chromadb",
    "sentence transformers",
    "semantic search",
    "httpx",
    "asyncio",
    "react",
    "streamlit",
    "machine learning",
    "llm",
    "tool calling",
    "oauth",
    "gmail api",
    "rest api",
    "microservices",
    "kubernetes",
    "git",
    "github actions",
]

ALIASES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "vector search": "semantic search",
    "retrieval augmented generation": "rag",
    "model-context-protocol": "model context protocol",
    "claude": "llm",
}


def normalize_skill(skill: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9+#.\s-]", " ", skill).strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return ALIASES.get(cleaned, cleaned)


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found: set[str] = set()
    for skill in CANONICAL_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.add(normalize_skill(skill))
    for alias, canonical in ALIASES.items():
        if alias in lowered:
            found.add(canonical)
    return sorted(found)


def extract_years_experience(text: str) -> int | None:
    matches = re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)\s+(?:of\s+)?experience", text.lower())
    if not matches:
        matches = re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)", text.lower())
    if not matches:
        return None
    return max(int(value) for value in matches)


def split_evidence_sentences(text: str, limit: int = 12) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    cleaned = [part.strip(" -\t") for part in parts if len(part.strip()) > 30]
    return cleaned[:limit]

