import json
import stat

from macle_meet.store import LocalStore


def test_store_keeps_source_revisions_and_exports_observations(tmp_path):
    private_dir = tmp_path / "private"
    database = private_dir / "macle.sqlite3"
    export = private_dir / "observations.jsonl"
    store = LocalStore(database)
    resource = {
        "name": "conferenceRecords/c1",
        "startTime": "2026-11-14T10:00:00Z",
        "space": {"name": "spaces/s1"},
    }
    assert store.add([resource], conference_name="conferenceRecords/c1") == 1
    assert store.add([resource], conference_name="conferenceRecords/c1") == 0
    changed = {**resource, "endTime": "2026-11-14T11:00:00Z"}
    assert store.add([changed], conference_name="conferenceRecords/c1") == 1
    assert store.export_jsonl(export) == 2
    rows = [json.loads(line) for line in export.read_text().splitlines()]
    assert all(row["source"]["conferenceRecord"] == "conferenceRecords/c1" for row in rows)
    assert all(row["payload"]["name"] == "conferenceRecords/c1" for row in rows)
    store.close()
    assert stat.S_IMODE(database.stat().st_mode) == 0o600
    assert stat.S_IMODE(export.stat().st_mode) == 0o600
    assert stat.S_IMODE(database.parent.stat().st_mode) == 0o700
