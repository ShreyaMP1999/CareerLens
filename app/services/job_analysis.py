from __future__ import annotations

import re

from app.schemas.domain import JobRequirements
from app.services.skills import extract_skills, extract_years_experience

PREFERRED_MARKERS = ("preferred", "nice to have", "bonus", "plus", "familiarity")


def analyze_job_description(description: str, title: str = "Role") -> JobRequirements:
    lowered = description.lower()
    preferred_start = min(
        [lowered.find(marker) for marker in PREFERRED_MARKERS if lowered.find(marker) >= 0],
        default=-1,
    )
    required_text = description if preferred_start < 0 else description[:preferred_start]
    preferred_text = "" if preferred_start < 0 else description[preferred_start:]
    skills = extract_skills(description)
    required: set[str] = set()
    preferred: set[str] = set()
    for skill in skills:
        if skill in extract_skills(preferred_text):
            preferred.add(skill)
        if skill in extract_skills(required_text) or skill not in preferred:
            required.add(skill)
    seniority = "senior" if re.search(r"\bsenior|staff|lead\b", description, re.I) else "mid"
    education = []
    if re.search(r"\b(bachelor|bs|ba)\b", description, re.I):
        education.append("bachelor")
    if re.search(r"\b(master|ms|phd|ph\.d)\b", description, re.I):
        education.append("advanced degree")
    return JobRequirements(
        title=title,
        description=description,
        required_skills=sorted(required),
        preferred_skills=sorted(preferred - required),
        years_experience=extract_years_experience(description),
        education=education,
        seniority=seniority,
    )
