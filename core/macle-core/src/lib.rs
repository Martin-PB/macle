//! Platform-independent MACLE session primitives.
//!
//! Capture APIs belong to platform adapters. This crate validates and records
//! the common session/observation contract; it does not acquire media itself.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::io::Write;
use thiserror::Error;

pub const MANIFEST_SCHEMA: &str = "macle.session-manifest/v1";
pub const OBSERVATION_SCHEMA: &str = "macle.observation/v1";

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SourceDescriptor {
    pub source_id: String,
    pub kind: String,
    pub status: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub detail: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ArtifactDescriptor {
    pub path: String,
    pub media_type: String,
    pub size_bytes: u64,
    pub sha256: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub started_at: Option<String>,
    #[serde(deserialize_with = "deserialize_nullable_required")]
    pub ended_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct SessionManifest {
    pub schema: String,
    pub session_id: String,
    pub platform: String,
    pub started_at: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ended_at: Option<String>,
    pub sources: Vec<SourceDescriptor>,
    pub artifacts: Vec<ArtifactDescriptor>,
    pub limitations: Vec<String>,
    pub authorization: AuthorizationRecord,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AuthorizationRecord {
    pub test_scope: String,
    pub egress: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct ObservationEnvelope {
    pub schema: String,
    pub observation_id: String,
    pub session_id: String,
    pub source_id: String,
    pub sequence: u64,
    pub kind: String,
    pub observed_at: String,
    pub payload: Value,
    pub provenance: Value,
}

#[derive(Debug, Error)]
pub enum CoreError {
    #[error("invalid JSON: {0}")]
    Json(#[from] serde_json::Error),
    #[error("invalid MACLE contract: {0}")]
    Invalid(String),
    #[error("observation sequence for source '{source_id}' must increase: got {got}, previous {previous}")]
    NonMonotonicSequence { source_id: String, got: u64, previous: u64 },
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
}

pub fn validate_manifest_json(input: &str) -> Result<SessionManifest, CoreError> {
    let manifest: SessionManifest = serde_json::from_str(input)?;
    if manifest.schema != MANIFEST_SCHEMA {
        return Err(CoreError::Invalid(format!("schema must be {MANIFEST_SCHEMA}")));
    }
    require_nonempty("session_id", &manifest.session_id)?;
    require_nonempty("platform", &manifest.platform)?;
    require_rfc3339("started_at", &manifest.started_at)?;
    if let Some(ended_at) = &manifest.ended_at { require_rfc3339("ended_at", ended_at)?; }
    let mut ids = std::collections::HashSet::new();
    for source in &manifest.sources {
        require_nonempty("source_id", &source.source_id)?;
        require_nonempty("source kind", &source.kind)?;
        if !ids.insert(&source.source_id) {
            return Err(CoreError::Invalid(format!("duplicate source_id: {}", source.source_id)));
        }
        if !matches!(source.status.as_str(), "available" | "unavailable" | "interrupted" | "not_requested") {
            return Err(CoreError::Invalid(format!("unsupported source status: {}", source.status)));
        }
    }
    for artifact in &manifest.artifacts {
        require_nonempty("artifact path", &artifact.path)?;
        if artifact.path.starts_with('/') || artifact.path.contains('\\')
            || artifact.path.split('/').any(|part| part == ".." || part.is_empty())
        {
            return Err(CoreError::Invalid(format!("artifact path must be a safe relative path: {}", artifact.path)));
        }
        require_nonempty("artifact media_type", &artifact.media_type)?;
        if let Some(started_at) = &artifact.started_at { require_rfc3339("artifact.started_at", started_at)?; }
        if let Some(ended_at) = &artifact.ended_at { require_rfc3339("artifact.ended_at", ended_at)?; }
        if artifact.sha256.len() != 64 || !artifact.sha256.bytes().all(|b| b.is_ascii_hexdigit()) {
            return Err(CoreError::Invalid(format!("artifact {} has an invalid SHA-256", artifact.path)));
        }
    }
    require_nonempty("authorization.test_scope", &manifest.authorization.test_scope)?;
    require_nonempty("authorization.egress", &manifest.authorization.egress)?;
    Ok(manifest)
}

pub fn validate_observation_json(input: &str) -> Result<ObservationEnvelope, CoreError> {
    let observation: ObservationEnvelope = serde_json::from_str(input)?;
    if observation.schema != OBSERVATION_SCHEMA {
        return Err(CoreError::Invalid(format!("schema must be {OBSERVATION_SCHEMA}")));
    }
    for (field, value) in [
        ("observation_id", observation.observation_id.as_str()),
        ("session_id", observation.session_id.as_str()),
        ("source_id", observation.source_id.as_str()),
        ("kind", observation.kind.as_str()),
        ("observed_at", observation.observed_at.as_str()),
    ] {
        require_nonempty(field, value)?;
    }
    require_rfc3339("observed_at", &observation.observed_at)?;
    Ok(observation)
}

fn deserialize_nullable_required<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    Option::<String>::deserialize(deserializer)
}

fn require_rfc3339(field: &str, value: &str) -> Result<(), CoreError> {
    time::OffsetDateTime::parse(value, &time::format_description::well_known::Rfc3339)
        .map(|_| ())
        .map_err(|error| CoreError::Invalid(format!("{field} must be RFC 3339: {error}")))
}

fn require_nonempty(field: &str, value: &str) -> Result<(), CoreError> {
    if value.trim().is_empty() {
        return Err(CoreError::Invalid(format!("{field} must not be empty")));
    }
    Ok(())
}

pub struct Sha256Accumulator {
    hasher: Sha256,
}

impl Sha256Accumulator {
    pub fn new() -> Self {
        Self { hasher: Sha256::new() }
    }

    pub fn update(&mut self, bytes: &[u8]) {
        self.hasher.update(bytes);
    }

    pub fn finalize_hex(self) -> String {
        format!("{:x}", self.hasher.finalize())
    }
}

impl Default for Sha256Accumulator {
    fn default() -> Self { Self::new() }
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    let mut accumulator = Sha256Accumulator::new();
    accumulator.update(bytes);
    accumulator.finalize_hex()
}

/// Append-only JSONL writer with per-source monotonic sequence enforcement.
pub struct ObservationLog<W: Write> {
    writer: W,
    session_id: String,
    last_sequence: HashMap<String, u64>,
}

impl<W: Write> ObservationLog<W> {
    pub fn new(writer: W, session_id: impl Into<String>) -> Self {
        Self { writer, session_id: session_id.into(), last_sequence: HashMap::new() }
    }

    pub fn append(&mut self, observation: &ObservationEnvelope) -> Result<(), CoreError> {
        validate_observation_json(&serde_json::to_string(observation)?)?;
        if observation.session_id != self.session_id {
            return Err(CoreError::Invalid("observation belongs to a different session".into()));
        }
        if let Some(previous) = self.last_sequence.get(&observation.source_id) {
            if observation.sequence <= *previous {
                return Err(CoreError::NonMonotonicSequence {
                    source_id: observation.source_id.clone(),
                    got: observation.sequence,
                    previous: *previous,
                });
            }
        }
        let mut line = serde_json::to_vec(observation)?;
        line.push(b'\n');
        self.writer.write_all(&line)?;
        self.last_sequence.insert(observation.source_id.clone(), observation.sequence);
        Ok(())
    }

    pub fn into_inner(self) -> W { self.writer }
}

#[cfg(target_arch = "wasm32")]
mod wasm_api {
    use super::*;
    use wasm_bindgen::prelude::*;

    #[wasm_bindgen]
    pub fn validate_manifest_json(input: &str) -> Result<String, JsValue> {
        super::validate_manifest_json(input)
            .map(|manifest| serde_json::to_string(&manifest).unwrap())
            .map_err(|error| JsValue::from_str(&error.to_string()))
    }

    #[wasm_bindgen]
    pub fn validate_observation_json(input: &str) -> Result<String, JsValue> {
        super::validate_observation_json(input)
            .map(|observation| serde_json::to_string(&observation).unwrap())
            .map_err(|error| JsValue::from_str(&error.to_string()))
    }

    #[wasm_bindgen]
    pub struct WasmSha256Accumulator {
        inner: super::Sha256Accumulator,
    }

    #[wasm_bindgen]
    impl WasmSha256Accumulator {
        #[wasm_bindgen(constructor)]
        pub fn new() -> WasmSha256Accumulator {
            WasmSha256Accumulator { inner: super::Sha256Accumulator::new() }
        }

        pub fn update(&mut self, input: &[u8]) {
            self.inner.update(input);
        }

        pub fn finalize_hex(self) -> String {
            self.inner.finalize_hex()
        }
    }

    #[wasm_bindgen]
    pub fn sha256_hex(input: &[u8]) -> String {
        super::sha256_hex(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn observation(source: &str, sequence: u64) -> ObservationEnvelope {
        ObservationEnvelope {
            schema: OBSERVATION_SCHEMA.into(),
            observation_id: format!("obs-{source}-{sequence}"),
            session_id: "session-1".into(),
            source_id: source.into(),
            sequence,
            kind: "capture.started".into(),
            observed_at: "2026-11-14T10:00:00Z".into(),
            payload: serde_json::json!({"synthetic": true}),
            provenance: serde_json::json!({"adapter": "test"}),
        }
    }

    #[test]
    fn sha256_matches_known_vector() {
        assert_eq!(sha256_hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    }

    #[test]
    fn observation_log_enforces_per_source_sequence_and_session() {
        let mut log = ObservationLog::new(Vec::new(), "session-1");
        log.append(&observation("screen", 1)).unwrap();
        log.append(&observation("audio", 1)).unwrap();
        log.append(&observation("screen", 2)).unwrap();
        let error = log.append(&observation("screen", 2)).unwrap_err();
        assert!(matches!(error, CoreError::NonMonotonicSequence { .. }));
        assert_eq!(log.into_inner().iter().filter(|b| **b == b'\n').count(), 3);
    }

    #[test]
    fn rejects_observation_from_another_session() {
        let mut log = ObservationLog::new(Vec::new(), "session-1");
        let mut event = observation("screen", 1);
        event.session_id = "session-2".into();
        assert!(log.append(&event).is_err());
    }

    #[test]
    fn validates_observation_contract() {
        let json = serde_json::to_string(&observation("screen", 1)).unwrap();
        assert!(validate_observation_json(&json).is_ok());
    }

    #[test]
    fn validates_shared_session_manifest_fixture() {
        let fixture = include_str!("../../../tests/fixtures/session-manifest-v1.json");
        let manifest = validate_manifest_json(fixture).unwrap();
        assert_eq!(manifest.session_id, "synthetic-session-001");
        assert_eq!(manifest.platform, "chrome");
    }

    #[test]
    fn rejects_unsafe_artifact_paths() {
        let fixture = include_str!("../../../tests/fixtures/session-manifest-v1.json");
        let mut manifest = validate_manifest_json(fixture).unwrap();
        manifest.artifacts.push(ArtifactDescriptor {
            path: "../escape.webm".into(),
            media_type: "video/webm".into(),
            size_bytes: 1,
            sha256: "a".repeat(64),
            started_at: None,
            ended_at: None,
        });
        let json = serde_json::to_string(&manifest).unwrap();
        assert!(validate_manifest_json(&json).is_err());
    }

    #[test]
    fn incremental_sha256_matches_one_shot_digest() {
        let mut incremental = Sha256Accumulator::new();
        incremental.update(b"a");
        incremental.update(b"b");
        incremental.update(b"c");
        assert_eq!(incremental.finalize_hex(), sha256_hex(b"abc"));
    }
}

#[cfg(target_os = "android")]
mod android_jni {
    use super::*;
    use jni::objects::{JClass, JString};
    use jni::sys::jstring;
    use jni::JNIEnv;

    fn validation_result<'local>(mut env: JNIEnv<'local>, input: JString<'local>, manifest: bool) -> jstring {
        let message = match env.get_string(&input) {
            Ok(value) => {
                let json = value.to_string_lossy().into_owned();
                let result = if manifest {
                    super::validate_manifest_json(&json).map(|_| ())
                } else {
                    super::validate_observation_json(&json).map(|_| ())
                };
                result.map(|_| String::new()).unwrap_or_else(|error| error.to_string())
            }
            Err(error) => error.to_string(),
        };
        env.new_string(message)
            .map(|value| value.into_raw())
            .unwrap_or(std::ptr::null_mut())
    }

    #[unsafe(no_mangle)]
    pub extern "system" fn Java_dev_macle_app_core_NativeCore_validateManifestJson<'local>(
        env: JNIEnv<'local>, _class: JClass<'local>, input: JString<'local>
    ) -> jstring {
        validation_result(env, input, true)
    }

    #[unsafe(no_mangle)]
    pub extern "system" fn Java_dev_macle_app_core_NativeCore_validateObservationJson<'local>(
        env: JNIEnv<'local>, _class: JClass<'local>, input: JString<'local>
    ) -> jstring {
        validation_result(env, input, false)
    }
}
