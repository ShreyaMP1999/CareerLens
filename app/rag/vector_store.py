from __future__ import annotations

from dataclasses import dataclass, field

from app.services.scoring import lexical_similarity


@dataclass
class RetrievedChunk:
    text: str
    score: float
    metadata: dict[str, str]


@dataclass
class LocalResumeVectorStore:
    """Small deterministic fallback used in demo/tests when Chroma is not configured."""

    chunks_by_user: dict[str, list[tuple[str, dict[str, str]]]] = field(default_factory=dict)

    def replace_resume(self, user_id: str, chunks: list[str], resume_id: str) -> None:
        self.chunks_by_user[user_id] = [
            (chunk, {"resume_id": resume_id, "chunk_index": str(index)})
            for index, chunk in enumerate(chunks)
        ]

    def remove_resume(self, user_id: str) -> None:
        self.chunks_by_user.pop(user_id, None)

    def query(self, user_id: str, query: str, k: int = 5) -> list[RetrievedChunk]:
        chunks = self.chunks_by_user.get(user_id, [])
        ranked = [
            RetrievedChunk(text=chunk, score=lexical_similarity(chunk, query), metadata=metadata)
            for chunk, metadata in chunks
        ]
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:k]

