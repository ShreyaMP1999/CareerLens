from __future__ import annotations

import math
from collections import Counter

from app.schemas.domain import JobRequirements, MatchReport, ResumeProfile

DEFAULT_WEIGHTS = {
    "required_skills": 0.40,
    "preferred_skills": 0.15,
    "experience": 0.20,
    "education": 0.10,
    "semantic_similarity": 0.15,
}


def _coverage(required: list[str], available: list[str]) -> tuple[float, list[str], list[str]]:
    if not required:
        return 1.0, [], []
    available_set = set(available)
    matched = [skill for skill in required if skill in available_set]
    missing = [skill for skill in required if skill not in available_set]
    return len(matched) / len(required), matched, missing


def lexical_similarity(left: str, right: str) -> float:
    left_tokens = Counter(token.lower() for token in left.split() if len(token) > 2)
    right_tokens = Counter(token.lower() for token in right.split() if len(token) > 2)
    if not left_tokens or not right_tokens:
        return 0.0
    shared = set(left_tokens) & set(right_tokens)
    numerator = sum(left_tokens[t] * right_tokens[t] for t in shared)
    left_norm = math.sqrt(sum(v * v for v in left_tokens.values()))
    right_norm = math.sqrt(sum(v * v for v in right_tokens.values()))
    return numerator / (left_norm * right_norm)


def match_resume_to_job(
    resume: ResumeProfile,
    job: JobRequirements,
    weights: dict[str, float] | None = None,
) -> MatchReport:
    active_weights = weights or DEFAULT_WEIGHTS
    req_score, required_matched, required_missing = _coverage(job.required_skills, resume.skills)
    pref_score, preferred_matched, _ = _coverage(job.preferred_skills, resume.skills)
    exp_score = 1.0 if resume.experience else 0.35
    if job.years_experience is not None and not resume.experience:
        exp_score = 0.2
    edu_score = 1.0
    if job.education:
        edu_score = 1.0 if resume.education else 0.45
    similarity = lexical_similarity(resume.raw_text, job.description)
    score = 100 * (
        active_weights["required_skills"] * req_score
        + active_weights["preferred_skills"] * pref_score
        + active_weights["experience"] * exp_score
        + active_weights["education"] * edu_score
        + active_weights["semantic_similarity"] * similarity
    )
    evidence = _select_evidence(resume, job.required_skills + job.preferred_skills)
    missing_or_uncertain = [f"No resume evidence found for {skill}." for skill in required_missing]
    suggestions = [
        f"Add a truthful bullet showing how you used {skill}, if you have that experience."
        for skill in required_missing[:5]
    ]
    if not suggestions:
        suggestions.append("Tailor the top resume summary to mirror the strongest verified job requirements.")
    explanation = (
        f"Transparent score from required skill coverage ({req_score:.0%}), preferred skill coverage "
        f"({pref_score:.0%}), experience evidence, education alignment, and lexical semantic overlap "
        f"({similarity:.0%}). This is not a hiring probability."
    )
    return MatchReport(
        overall_score=round(min(score, 100.0), 2),
        required_skills_matched=required_matched,
        required_skills_missing=required_missing,
        preferred_skills_matched=preferred_matched,
        relevant_experience=evidence[:5],
        missing_or_uncertain=missing_or_uncertain,
        suggestions=suggestions,
        score_explanation=explanation,
        evidence=evidence,
        weights=active_weights,
    )


def _select_evidence(resume: ResumeProfile, skills: list[str]) -> list[str]:
    evidence: list[str] = []
    for chunk in resume.chunks or resume.experience:
        lowered = chunk.lower()
        if any(skill in lowered for skill in skills):
            evidence.append(chunk)
    if not evidence:
        evidence = resume.experience[:3] or resume.chunks[:3]
    return evidence[:6]


def identify_skill_gaps(resume: ResumeProfile, job: JobRequirements) -> list[str]:
    _, _, missing_required = _coverage(job.required_skills, resume.skills)
    _, _, missing_preferred = _coverage(job.preferred_skills, resume.skills)
    return missing_required + [f"{skill} (preferred)" for skill in missing_preferred]

