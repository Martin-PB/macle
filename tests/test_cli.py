from macle_meet.cli import build_parser


def test_sync_accepts_meeting_code_for_active_conference_lookup():
    args = build_parser().parse_args(["sync", "--meeting-code", "abc-mnop-xyz"])
    assert args.command == "sync"
    assert args.meeting_code == "abc-mnop-xyz"
    assert args.conference_record is None


def test_sync_rejects_multiple_conference_lookup_modes():
    parser = build_parser()
    try:
        parser.parse_args([
            "sync",
            "--meeting-code", "abc-mnop-xyz",
            "--conference-record", "conferenceRecords/c1",
        ])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("lookup modes should be mutually exclusive")



def test_oauth_config_directory_is_owner_only(tmp_path):
    import stat

    from macle_meet.cli import ensure_private_config_directory

    directory = tmp_path / "macle-meet"
    ensure_private_config_directory(directory)
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700


def test_transcribe_command_defaults_to_local_cpu_int8():
    args = build_parser().parse_args([
        "transcribe",
        "--media", "capture.webm",
        "--manifest", "capture.manifest.json",
    ])
    assert args.command == "transcribe"
    assert args.model == "small"
    assert args.device == "cpu"
    assert args.compute_type is None
    assert args.language is None


def test_transcribe_command_accepts_conference_resource():
    args = build_parser().parse_args([
        "transcribe",
        "--media", "capture.webm",
        "--manifest", "capture.manifest.json",
        "--conference-record", "conferenceRecords/c1",
    ])
    assert args.conference_record == "conferenceRecords/c1"



def test_watch_command_defaults_to_fifteen_second_local_polling():
    args = build_parser().parse_args(["watch", "--meeting-code", "abc-mnop-xyz"])
    assert args.command == "watch"
    assert args.meeting_code == "abc-mnop-xyz"
    assert args.interval == 15.0
    assert args.duration is None


def test_watch_polls_until_conference_ends_and_exports_revisions(tmp_path, monkeypatch):
    import json
    from argparse import Namespace
    from types import SimpleNamespace

    import macle_meet.cli as cli

    class FakeClient:
        def __init__(self, session):
            self.calls = 0

        def get_space(self, name):
            return {
                "name": "spaces/stable-id",
                "activeConference": {"conferenceRecord": "conferenceRecords/c1"},
            }

        def get(self, name):
            self.calls += 1
            conference = {"name": name, "startTime": "2026-11-14T10:00:00Z"}
            if self.calls >= 2:
                conference["endTime"] = "2026-11-14T10:02:00Z"
            return conference

        def collect_participant_state(self, conference):
            return [
                {"name": "conferenceRecords/c1/participants/p1"},
                {
                    "name": "conferenceRecords/c1/participants/p1/participantSessions/s1",
                    "startTime": "2026-11-14T10:00:01Z",
                },
            ]

    clock = {"now": 0.0}
    monkeypatch.setattr(cli, "load_credentials", lambda path: object())
    monkeypatch.setattr(cli, "MeetClient", FakeClient)
    monkeypatch.setattr(cli.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(cli.time, "sleep", lambda seconds: clock.__setitem__("now", clock["now"] + seconds))

    database = tmp_path / "macle.sqlite3"
    export = tmp_path / "observations.jsonl"
    args = Namespace(
        token_file=tmp_path / "token.json",
        meeting_code="abc-mnop-xyz",
        space=None,
        conference_record=None,
        interval=1.0,
        duration=None,
        database=database,
        export=export,
    )

    assert cli.run_watch(args) == 0
    rows = [json.loads(line) for line in export.read_text().splitlines()]
    assert len(rows) == 4
    assert sum(row["payload"].get("endTime") is not None for row in rows) == 1
