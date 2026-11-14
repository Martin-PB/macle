import json
from pathlib import Path


def test_chrome_extension_is_local_and_meet_scoped():
    manifest_path = (
        Path(__file__).parents[1]
        / "connectors/google-meet/chrome-extension/manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert manifest["minimum_chrome_version"] == "116"
    assert "tabCapture" in manifest["permissions"]
    assert "offscreen" in manifest["permissions"]
    assert "downloads" in manifest["permissions"]
    assert manifest["host_permissions"] == ["https://meet.google.com/*"]
    assert manifest["options_ui"]["page"] == "options.html"
    assert "default_popup" not in manifest["action"]
