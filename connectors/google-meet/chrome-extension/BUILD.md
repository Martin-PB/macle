# Chrome extension build

The extension now validates its session manifest with the shared Rust core compiled to WebAssembly. Build the module before loading the unpacked extension.

From the repository root:

```sh
sh scripts/test-wasm-core.sh
```

Then load `connectors/google-meet/chrome-extension` from `chrome://extensions` with Developer mode enabled.

The generated `core-wasm/` directory is a local build artifact and is not committed. A missing module prevents capture from starting; the extension does not silently substitute a different validator.

The existing synthetic-test attestation remains required. The extension captures only the selected rendered Meet tab, and its output is local-only.
