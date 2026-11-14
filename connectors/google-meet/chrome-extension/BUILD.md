# Chrome extension build

The extension validates its session manifest with the shared Rust core compiled to WebAssembly. Build the module before loading the extension.

## Reproducible package

See [the shared installation guide](../../../docs/INSTALLATION.md#chrome) for prerequisites and setup.

From the repository root:

~~~sh
cargo install wasm-pack
sh scripts/package-chrome-extension.sh
~~~

The script builds and tests the WASM module, syntax-checks the extension JavaScript, and creates dist/macle-chrome-extension.zip. It also leaves the generated core-wasm/ directory in place for loading the unpacked extension.

To load the unpacked extension, open chrome://extensions, enable Developer mode, and select Load unpacked. Choose connectors/google-meet/chrome-extension.

The generated core-wasm/ directory is a local build artifact and is not committed. A missing module prevents capture from starting; the extension does not silently substitute a different validator.

The existing synthetic-test attestation remains required. The extension captures only the selected rendered Meet tab, and its output is local-only. Microphone capture is optional, off by default, and may only be enabled for synthetic test audio under the current Stage A boundary.
