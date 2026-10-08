from __future__ import annotations

import io
import re
from pathlib import Path

from app.schemas.domain import ResumeProfile
from app.services.skills import extract_skills, split_evidence_sentences


class ResumeParseError(ValueError):
    pass


def _read_pdf(data: bytes) -> str:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ResumeParseError("PyMuPDF is required for PDF parsing.") from exc
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def _read_docx(data: bytes) -> str:
    try:
        from docx import Document  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ResumeParseError("python-docx is required for DOCX parsing.") from exc
    document = Document(io.BytesIO(data))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_text_from_file(path: str | Path, max_mb: int = 8) -> str:
    file_path = Path(path)
    data = file_path.read_bytes()
    if len(data) > max_mb * 1024 * 1024:
        raise ResumeParseError(f"Resume exceeds {max_mb} MB upload limit.")
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(data)
    if suffix == ".docx":
        return _read_docx(data)
    if suffix in {".txt", ".md"}:
        return data.decode("utf-8", errors="replace")
    raise ResumeParseError(f"Unsupported resume file type: {suffix}")


def chunk_text(text: str, chunk_size: int = 750, overlap: int = 100) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks


def parse_resume_text(text: str) -> ResumeProfile:
    lowered = text.lower()
    education = []
    for marker in ["bachelor", "master", "ph.d", "university", "college"]:
        if marker in lowered:
            education.append(marker)
    experience = [
        sentence
        for sentence in split_evidence_sentences(text)
        if re.search(r"\b(built|developed|implemented|led|designed|created|managed)\b", sentence, re.I)
    ]
    projects = [
        sentence
        for sentence in split_evidence_sentences(text)
        if re.search(r"\b(project|portfolio|prototype|dashboard|api)\b", sentence, re.I)
    ]
    skills = extract_skills(text)
    return ResumeProfile(
        raw_text=text,
        skills=skills,
        experience=experience[:8],
        education=education,
        projects=projects[:8],
        technologies=skills,
        chunks=chunk_text(text, chunk_size=90, overlap=15),
    )

