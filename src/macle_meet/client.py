"""Small Google Meet REST API v2 client with pagination."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

API_ROOT = "https://meet.googleapis.com/v2"


class MeetApiError(RuntimeError):
    """An API request failed with a useful, sanitized diagnostic."""


class MeetClient:
    def __init__(self, session: requests.Session, base_url: str = API_ROOT):
        self.session = session
        self.base_url = base_url.rstrip("/")

    def get(self, resource: str) -> dict[str, Any]:
        return self._request(resource, {})

    def list_all(
        self,
        resource: str,
        collection: str,
        *,
        params: dict[str, Any] | None = None,
        page_size: int = 100,
        response_key: str | None = None,
    ) -> list[dict[str, Any]]:
        query = dict(params or {})
        query["pageSize"] = min(max(page_size, 1), 100)
        items: list[dict[str, Any]] = []
        while True:
            page = self._request(resource, query)
            # Google uses camelCase collection keys. Accept the lower-case
            # variant too, since generated examples have historically varied.
            key = response_key or collection
            values = page.get(key, [])
            if not isinstance(values, list):
                raise MeetApiError(
                    f"Unexpected response for {resource}: missing list '{collection}'."
                )
            items.extend(values)
            token = page.get("nextPageToken")
            if not token:
                return items
            query["pageToken"] = token

    def get_space(self, space_name: str) -> dict[str, Any]:
        """Get a space by resource name or meeting-code alias."""
        return self.get(space_name)

    def list_conferences(
        self, *, since: str | None = None, conference_name: str | None = None
    ) -> list[dict[str, Any]]:
        if conference_name:
            return [self.get(conference_name)]
        params: dict[str, Any] = {}
        if since:
            params["filter"] = f'start_time>="{since}"'
        return self.list_all("conferenceRecords", "conferenceRecords", params=params)

    def collect_conference(self, conference: dict[str, Any]) -> list[dict[str, Any]]:
        """Collect conference, participants, sessions, and available artifacts."""
        name = conference.get("name")
        if not name:
            raise MeetApiError("Conference record has no resource name.")
        records: list[dict[str, Any]] = [conference]

        participants = self.list_all(f"{name}/participants", "participants")
        records.extend(participants)

        for participant in participants:
            participant_name = participant.get("name")
            if participant_name:
                records.extend(
                    self.list_all(f"{participant_name}/participantSessions", "participantSessions")
                )

        recordings = self.list_all(f"{name}/recordings", "recordings")
        transcripts = self.list_all(f"{name}/transcripts", "transcripts")
        smart_notes = self.list_all(f"{name}/smartNotes", "smartNotes")
        records.extend(recordings)
        records.extend(transcripts)
        records.extend(smart_notes)

        for transcript in transcripts:
            transcript_name = transcript.get("name")
            if transcript_name:
                records.extend(
                    self.list_all(f"{transcript_name}/entries", "transcriptEntries", page_size=100)
                )
        return records

    def collect_participant_state(self, conference: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch participant and participant-session resources for one poll."""
        conference_name = conference.get("name")
        if not conference_name:
            raise MeetApiError("Conference record has no resource name.")
        participants = self.list_all(
            f"{conference_name}/participants", "participants"
        )
        resources: list[dict[str, Any]] = list(participants)
        for participant in participants:
            participant_name = participant.get("name")
            if participant_name:
                resources.extend(
                    self.list_all(
                        f"{participant_name}/participantSessions",
                        "participantSessions",
                    )
                )
        return resources

    def _request(self, resource: str, params: dict[str, Any]) -> dict[str, Any]:
        path = resource.strip("/")
        url = f"{self.base_url}/{quote(path, safe='/')}"
        response = self.session.get(url, params=params, timeout=30)
        if not response.ok:
            detail = response.text[:1200]
            hint = ""
            if response.status_code == 403:
                hint = (
                    " Check that the Google Meet API is enabled, the OAuth "
                    "scope meetings.space.readonly was granted, and the signed-in "
                    "user has access to this conference. The list endpoint only "
                    "discovers conferences organized by the signed-in user."
                )
            elif response.status_code == 404:
                hint = " The resource may be unavailable, expired, or inaccessible."
            raise MeetApiError(
                f"Google Meet API returned HTTP {response.status_code} for "
                f"{path}: {detail}{hint}"
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise MeetApiError(f"Google Meet API returned invalid JSON for {path}.") from exc
        if not isinstance(payload, dict):
            raise MeetApiError(f"Google Meet API returned a non-object for {path}.")
        return payload
