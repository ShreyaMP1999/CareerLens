from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.schemas.domain import ApplicationRecord, ApplicationStatus
from app.services.job_search import normalize_job_url


@dataclass
class StatusEvent:
    application_id: str
    from_status: ApplicationStatus
    to_status: ApplicationStatus
    changed_at: datetime
    note: str = ""


@dataclass
class ApplicationTracker:
    records: dict[str, ApplicationRecord] = field(default_factory=dict)
    history: list[StatusEvent] = field(default_factory=list)

    def save_job(self, record: ApplicationRecord) -> ApplicationRecord:
        duplicate = self._find_by_url(record.job_url)
        if duplicate:
            return duplicate
        self.records[str(record.id)] = record
        return record

    def update_status(
        self,
        application_id: str,
        new_status: ApplicationStatus,
        note: str = "",
    ) -> ApplicationRecord:
        record = self.records[application_id]
        old_status = record.status
        record.status = new_status
        record.updated_at = datetime.now(UTC)
        self.history.append(
            StatusEvent(application_id, old_status, new_status, record.updated_at, note)
        )
        return record

    def get_due_followups(self, now: datetime | None = None) -> list[ApplicationRecord]:
        current = now or datetime.now(UTC)
        return [
            record
            for record in self.records.values()
            if record.follow_up_date and record.follow_up_date <= current
        ]

    def analytics(self) -> dict[str, object]:
        statuses = Counter(record.status.value for record in self.records.values())
        companies = Counter(record.company for record in self.records.values())
        total = len(self.records)
        applied = sum(
            count
            for status, count in statuses.items()
            if status
            in {
                ApplicationStatus.APPLIED.value,
                ApplicationStatus.RECRUITER_SCREEN.value,
                ApplicationStatus.TECHNICAL_INTERVIEW.value,
                ApplicationStatus.HIRING_MANAGER_INTERVIEW.value,
                ApplicationStatus.FINAL_INTERVIEW.value,
                ApplicationStatus.OFFER.value,
            }
        )
        interviews = sum(
            statuses[status.value]
            for status in [
                ApplicationStatus.RECRUITER_SCREEN,
                ApplicationStatus.TECHNICAL_INTERVIEW,
                ApplicationStatus.HIRING_MANAGER_INTERVIEW,
                ApplicationStatus.FINAL_INTERVIEW,
                ApplicationStatus.OFFER,
            ]
        )
        return {
            "total_jobs_discovered": total,
            "total_applications_submitted": applied,
            "interviews_received": interviews,
            "response_rate": round(interviews / applied, 3) if applied else 0,
            "interview_conversion_rate": round(interviews / total, 3) if total else 0,
            "applications_by_company": dict(companies),
            "applications_by_status": dict(statuses),
        }

    def _find_by_url(self, url: str) -> ApplicationRecord | None:
        normalized = normalize_job_url(url)
        for record in self.records.values():
            if normalize_job_url(record.job_url) == normalized:
                return record
        return None
