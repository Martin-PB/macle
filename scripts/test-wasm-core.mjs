import { readFile } from "node:fs/promises";
import init, {
  validate_manifest_json,
  validate_observation_json,
  WasmSha256Accumulator
} from "../connectors/google-meet/chrome-extension/core-wasm/macle_core.js";

const wasmBytes = await readFile(new URL("../connectors/google-meet/chrome-extension/core-wasm/macle_core_bg.wasm", import.meta.url));
await init(wasmBytes);

const manifest = await readFile(new URL("../tests/fixtures/session-manifest-v1.json", import.meta.url), "utf8");
const observation = await readFile(new URL("../tests/fixtures/observation-v1.json", import.meta.url), "utf8");
validate_manifest_json(manifest);
validate_observation_json(observation);

const digest = new WasmSha256Accumulator();
digest.update(new TextEncoder().encode("a"));
digest.update(new TextEncoder().encode("b"));
digest.update(new TextEncoder().encode("c"));
const actual = digest.finalize_hex();
const expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
if (actual !== expected) throw new Error(`Incremental SHA-256 mismatch: ${actual}`);

console.log("MACLE WASM contract fixtures and incremental SHA-256: PASS");
