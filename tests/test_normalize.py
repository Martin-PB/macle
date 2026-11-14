from macle_meet.normalize import normalize_resource, sanitize_space_resource


def test_transcript_entry_preserves_source_and_text():
    resource = {
        "name": "conferenceRecords/c1/transcripts/t1/entries/e1",
        "participant": "conferenceRecords/c1/participants/p1",
        "text": "Synthetic hello",
        "languageCode": "en-US",
        "startTime": "2026-11-14T10:00:00Z",
        "endTime": "2026-11-14T10:00:02Z",
    }
    result = normalize_resource(
        resource,
        conference_name="conferenceRecords/c1",
        retrieved_at="2026-11-14T10:01:00Z",
    )
    assert result["schema"] == "macle.observation/v0"
    assert result["source"]["resourceType"] == "transcript_entry"
    assert result["source"]["resourceName"] == resource["name"]
    assert result["source"]["conferenceRecord"] == "conferenceRecords/c1"
    assert result["observedAt"] == resource["startTime"]
    assert result["retrievedAt"] == "2026-11-14T10:01:00Z"
    assert result["content"] == "Synthetic hello"
    assert result["payload"] == resource


def test_participant_and_session_are_distinct():
    participant = {
        "name": "conferenceRecords/c1/participants/p1",
        "earliestStartTime": "2026-11-14T10:00:00Z",
    }
    session = {
        "name": "conferenceRecords/c1/participants/p1/participantSessions/s1",
        "startTime": "2026-11-14T10:00:00Z",
    }
    p = normalize_resource(participant, conference_name="conferenceRecords/c1")
    s = normalize_resource(session, conference_name="conferenceRecords/c1")
    assert p["source"]["resourceType"] == "participant"
    assert s["source"]["resourceType"] == "participant_session"
    assert p["id"] != s["id"]


def test_recording_is_reference_not_captured_media():
    resource = {
        "name": "conferenceRecords/c1/recordings/r1",
        "state": {"status": "FILE_GENERATED"},
    }
    result = normalize_resource(resource, conference_name="conferenceRecords/c1")
    assert result["modality"] == "media_artifact_reference"
    assert "not a raw audio/video observation" in result["limitations"][0]


def test_meeting_space_is_not_misclassified_as_conference_record():
    resource = {
        "name": "spaces/abc-mnop-xyz",
        "meetingCode": "abc-mnop-xyz",
        "activeConference": {
            "conferenceRecord": "conferenceRecords/c1"
        },
    }
    result = normalize_resource(resource, conference_name="conferenceRecords/c1")
    assert result["source"]["resourceType"] == "meeting_space"
    assert result["payload"] == resource


def test_space_snapshot_does_not_persist_short_lived_meeting_code_or_uri():
    resource = {
        "name": "spaces/space-id",
        "meetingCode": "abc-mnop-xyz",
        "meetingUri": "https://meet.google.com/abc-mnop-xyz",
        "activeConference": {"conferenceRecord": "conferenceRecords/c1"},
    }
    safe = sanitize_space_resource(resource)
    assert safe["name"] == "spaces/space-id"
    assert safe["activeConference"] == resource["activeConference"]
    assert "meetingCode" not in safe
    assert "meetingUri" not in safe
