from app.rag.vector_store import LocalResumeVectorStore


def test_resume_retrieval_recall_at_k():
    store = LocalResumeVectorStore()
    chunks = [
        "Built FastAPI and PostgreSQL APIs for backend services.",
        "Created RAG pipelines with ChromaDB and sentence transformers.",
        "Designed React components for a dashboard.",
    ]
    store.replace_resume("user-1", chunks, "resume-1")
    results = store.query("user-1", "semantic search with ChromaDB", k=2)
    assert any("ChromaDB" in result.text for result in results)
    assert store.query("user-2", "ChromaDB", k=2) == []

