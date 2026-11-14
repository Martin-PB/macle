# Shared conformance fixtures

The fixtures in this directory are language-neutral contract examples.

- `fixtures/session-manifest-v1.json` is consumed by Rust unit tests and the Android manifest-import smoke test; it is also validated by the built WASM module in `scripts/test-wasm-core.mjs`.
- `fixtures/observation-v1.json` is consumed by Rust unit tests and the WASM smoke test.

Run the native core tests from the repository root:

```sh
cargo test --workspace
```

Run the WASM conformance smoke test (requires Rust, wasm-pack, the WASM target and Node.js):

```sh
sh scripts/test-wasm-core.sh
```

The Chrome extension's normal capture path uses this same WASM API at runtime.
