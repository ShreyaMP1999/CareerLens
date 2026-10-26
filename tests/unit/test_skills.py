import pytest

from app.services.skills import extract_skills


@pytest.mark.parametrize(
    "text",
    ["PostgresQLish", "postgraduate", "claudette", "myclaude2", "vector searches"],
)
def test_skill_aliases_do_not_match_inside_other_words(text):
    assert extract_skills(text) == []


def test_skill_aliases_match_case_insensitively_at_punctuation_boundaries():
    assert extract_skills("Used (POSTGRES), Claude/LLM, and vector search.") == [
        "llm",
        "postgresql",
        "semantic search",
    ]


def test_multiword_aliases_and_canonical_skills_are_deduplicated():
    text = (
        "Postgres and PostgreSQL; retrieval augmented generation (RAG); "
        "model-context-protocol; Python and python."
    )
    assert extract_skills(text) == ["model context protocol", "postgresql", "python", "rag"]
