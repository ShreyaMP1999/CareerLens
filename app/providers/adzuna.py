from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.config import Settings
from app.schemas.domain import JobPosting, WorkArrangement


class MissingAdzunaCredentials(RuntimeError):
    pass


class AdzunaJobProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str, location: str = "", results_per_page: int = 20) -> list[JobPosting]:
        if not self.settings.adzuna_app_id or not self.settings.adzuna_app_key:
            raise MissingAdzunaCredentials("Set ADZUNA_APP_ID and ADZUNA_APP_KEY for live job search.")
        import httpx

        url = (
            f"https://api.adzuna.com/v1/api/jobs/{self.settings.adzuna_country}/search/1"
        )
        params = {
            "app_id": self.settings.adzuna_app_id,
            "app_key": self.settings.adzuna_app_key,
            "what": query,
            "where": location,
            "results_per_page": results_per_page,
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            if response.status_code == 429:
                raise RuntimeError("Adzuna rate limit reached; retry later or reduce search volume.")
            response.raise_for_status()
            payload = response.json()
        return [self._parse_result(item) for item in payload.get("results", [])]

    def _parse_result(self, item: dict[str, Any]) -> JobPosting:
        created = item.get("created")
        posted_at = datetime.fromisoformat(created.replace("Z", "+00:00")) if created else None
        return JobPosting(
            title=item.get("title", "Unknown title"),
            company=item.get("company", {}).get("display_name", "Unknown company"),
            location=item.get("location", {}).get("display_name", "Unknown location"),
            description=item.get("description", ""),
            url=item.get("redirect_url", ""),
            source="adzuna",
            provider_id=str(item.get("id") or ""),
            posted_at=posted_at,
            salary_min=item.get("salary_min"),
            salary_max=item.get("salary_max"),
            work_arrangement=_infer_arrangement(item.get("description", ""), item.get("location", {}).get("display_name", "")),
            metadata={"category": item.get("category", {}).get("label", "")},
        )


def _infer_arrangement(description: str, location: str) -> WorkArrangement:
    text = f"{description} {location}".lower()
    if "remote" in text:
        return WorkArrangement.REMOTE
    if "hybrid" in text:
        return WorkArrangement.HYBRID
    if location:
        return WorkArrangement.ONSITE
    return WorkArrangement.UNKNOWN

