from __future__ import annotations

from dataclasses import dataclass

from app.schemas.domain import JobRequirements, ResumeProfile
from app.services.scoring import match_resume_to_job


@dataclass
class EmailDraft:
    subject: str
    body: str
    evidence_used: list[str]
    unverified_claims: list[str]
    draft_type: str = "initial_recruiter_outreach"


def validate_email_claims(body: str, evidence: list[str]) -> list[str]:
    claims = []
    lowered_evidence = " ".join(evidence).lower()
    for risky in ["expert", "guaranteed", "perfect fit", "led a team of", "10 years"]:
        if risky in body.lower() and risky not in lowered_evidence:
            claims.append(f"Unverified or inflated phrase: {risky}")
    return claims


def draft_recruiter_email(
    resume: ResumeProfile,
    job: JobRequirements,
    company_name: str,
    recruiter_name: str | None = None,
    tone: str = "warm and concise",
    draft_type: str = "initial_recruiter_outreach",
) -> EmailDraft:
    report = match_resume_to_job(resume, job)
    top_skills = (report.required_skills_matched + report.preferred_skills_matched)[:3]
    greeting = f"Hi {recruiter_name}," if recruiter_name else "Hi there,"
    skill_phrase = ", ".join(top_skills) if top_skills else "relevant backend and AI engineering work"
    evidence = report.evidence[:3]
    evidence_sentence = evidence[0] if evidence else "My background aligns with the role requirements."
    subject = f"Interest in {job.title} at {company_name}"
    body = (
        f"{greeting}\n\n"
        f"I’m interested in the {job.title} role at {company_name}. My strongest verified fit is "
        f"{skill_phrase}. One relevant example from my background: {evidence_sentence}\n\n"
        "I’d welcome the chance to discuss how this experience could support the team’s work. "
        "Thanks for your time.\n\n"
        "Best,\n"
        "Shreya"
    )
    if tone == "direct":
        body = body.replace("I’d welcome the chance to discuss", "I would like to discuss")
    unverified = validate_email_claims(body, evidence)
    return EmailDraft(subject=subject, body=body, evidence_used=evidence, unverified_claims=unverified, draft_type=draft_type)


def generate_email_variations(base: EmailDraft) -> list[EmailDraft]:
    shorter = EmailDraft(
        subject=base.subject,
        body="\n\n".join(base.body.split("\n\n")[:2]) + "\n\nBest,\nShreya",
        evidence_used=base.evidence_used,
        unverified_claims=base.unverified_claims,
        draft_type=base.draft_type,
    )
    followup = EmailDraft(
        subject=f"Following up: {base.subject}",
        body=(
            "Hi there,\n\n"
            "I wanted to follow up on my note about this role. I remain interested and would be "
            "glad to share more detail on the relevant experience below.\n\n"
            f"Evidence used: {base.evidence_used[0] if base.evidence_used else 'resume evidence unavailable'}\n\n"
            "Best,\nShreya"
        ),
        evidence_used=base.evidence_used,
        unverified_claims=[],
        draft_type="follow_up",
    )
    return [base, shorter, followup]


def create_gmail_draft(*_: object, authorized: bool = False) -> dict[str, str]:
    if not authorized:
        return {"status": "approval_required", "message": "Gmail draft creation requires explicit user authorization."}
    return {"status": "not_configured", "message": "Configure Gmail OAuth credentials before creating drafts."}

