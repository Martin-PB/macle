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
