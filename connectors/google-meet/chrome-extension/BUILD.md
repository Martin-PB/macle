# Chrome extension build and distribution

## Install a prebuilt release (recommended for users)

Once the first release workflow has completed, download the versioned ZIP from [MACLE Chrome releases](https://github.com/Martin-PB/macle/releases). The ZIP already contains the compiled shared Rust/WASM runtime. Users do not need Rust, Cargo, wasm-pack, Node.js, or a local build environment.

1. Extract the ZIP into a permanent folder.
2. Open `chrome://extensions` and enable **Developer mode**.
3. Click **Load unpacked** and select the extracted folder containing `manifest.json`.
4. Open the extension options and explicitly attest to synthetic-only testing.
5. Open a synthetic Google Meet test meeting and use the toolbar icon to start/stop capture.

This is an unpacked developer-mode installation, not a Chrome Web Store installation. Keep the extracted folder in place. To update, extract a newer release and reload or replace the unpacked extension.

The release includes `SHA256SUMS.txt` and `BUILD-PROVENANCE.txt`. Verify the archive checksum before installation when desired.

## Reproducible source build (maintainers and contributors)

The extension validates its session manifest with the shared Rust core compiled to WebAssembly. Build the module before loading the extension.

From the repository root:

~~~sh
cargo install wasm-pack
sh scripts/package-chrome-extension.sh
~~~

The script builds and tests the WASM module, syntax-checks the extension JavaScript, and creates `dist/macle-chrome-extension.zip`. It also leaves the generated `core-wasm/` directory in place for loading the unpacked extension.

To load the source-tree version, open `chrome://extensions`, enable Developer mode, and select **Load unpacked**. Choose `connectors/google-meet/chrome-extension`.

The generated `core-wasm/` directory is a local build artifact and is not committed. A missing module prevents capture from starting; the extension does not silently substitute a different validator.

## Release process

A maintainer can publish without a local build or Git command by opening **Actions → MACLE Chrome extension release → Run workflow** on the `main` branch, setting **Publish a versioned GitHub Release** to true, and entering the version from `manifest.json`. Alternatively, pushing a tag named `macle-chrome-vX.Y.Z` publishes the same release. The release workflow:

- runs the native Rust workspace tests;
- builds and exercises the exact WASM module used by the extension;
- syntax-checks the extension JavaScript through the packaging script;
- verifies that the ZIP contains the Manifest V3 descriptor and non-empty WASM runtime;
- records SHA-256 checksums and build provenance;
- publishes the ZIP and verification files as GitHub Release assets.

The requested version must match `version` in `manifest.json`. A manual workflow dispatch with publishing disabled builds and uploads a temporary artifact but does not publish a release. The workflow only allows manual publication from `main`, and creates the matching tag and GitHub Release after all build and archive checks pass.

## Capture and authorization boundary

The existing synthetic-test attestation remains required. The extension captures only the selected rendered Meet tab, and its output is local-only. Microphone capture is optional, off by default, and may only be enabled for synthetic test audio under the current Stage A boundary.

A successful build/package check does not prove that tab audio is available in every Meet/Chrome configuration. The browser smoke test remains a separate operational acceptance gate.
