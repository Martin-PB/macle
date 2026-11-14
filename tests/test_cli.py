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
