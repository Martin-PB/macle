from macle_meet.client import MeetClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.ok = True

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, dict(params or {})))
        if len(self.calls) == 1:
            return FakeResponse({"conferenceRecords": [{"name": "conferenceRecords/c1"}], "nextPageToken": "next"})
        return FakeResponse({"conferenceRecords": [{"name": "conferenceRecords/c2"}]})


def test_pagination_collects_all_pages():
    session = FakeSession()
    client = MeetClient(session, base_url="https://example.test/v2")
    result = client.list_all("conferenceRecords", "conferenceRecords")
    assert [item["name"] for item in result] == [
        "conferenceRecords/c1",
        "conferenceRecords/c2",
    ]
    assert session.calls[1][1]["pageToken"] == "next"


class CollectionSession:
    def get(self, url, params=None, timeout=None):
        if url.endswith("/participants"):
            return FakeResponse({"participants": [{"name": "conferenceRecords/c1/participants/p1"}]})
        if url.endswith("/participantSessions"):
            return FakeResponse({"participantSessions": [{"name": "conferenceRecords/c1/participants/p1/participantSessions/s1"}]})
        if url.endswith("/recordings"):
            return FakeResponse({"recordings": []})
        if url.endswith("/transcripts"):
            return FakeResponse({"transcripts": [{"name": "conferenceRecords/c1/transcripts/t1"}]})
        if url.endswith("/smartNotes"):
            return FakeResponse({"smartNotes": []})
        if url.endswith("/entries"):
            return FakeResponse({"transcriptEntries": [{"name": "conferenceRecords/c1/transcripts/t1/entries/e1", "text": "synthetic"}]})
        raise AssertionError(f"Unexpected URL: {url}")


def test_collect_conference_reads_transcript_entries_and_sessions():
    client = MeetClient(CollectionSession(), base_url="https://example.test/v2")
    resources = client.collect_conference({"name": "conferenceRecords/c1"})
    names = {resource["name"] for resource in resources}
    assert "conferenceRecords/c1/participants/p1/participantSessions/s1" in names
    assert "conferenceRecords/c1/transcripts/t1/entries/e1" in names



class ParticipantStateSession:
    def get(self, url, params=None, timeout=None):
        if url.endswith("/participants"):
            return FakeResponse({
                "participants": [{"name": "conferenceRecords/c1/participants/p1"}]
            })
        if url.endswith("/participantSessions"):
            return FakeResponse({
                "participantSessions": [{
                    "name": "conferenceRecords/c1/participants/p1/participantSessions/s1",
                    "startTime": "2026-11-14T10:00:00Z",
                }]
            })
        raise AssertionError(f"Unexpected URL: {url}")


def test_collect_participant_state_reads_participants_and_sessions():
    client = MeetClient(ParticipantStateSession(), base_url="https://example.test/v2")
    resources = client.collect_participant_state({"name": "conferenceRecords/c1"})
    assert [resource["name"] for resource in resources] == [
        "conferenceRecords/c1/participants/p1",
        "conferenceRecords/c1/participants/p1/participantSessions/s1",
    ]
