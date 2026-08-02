use serde_json::Value;
use std::collections::HashMap;
use std::process::Command;

/// Hardware trust abstractions for Z-12.
///
/// This module provides a small abstraction layer for platform-backed
/// hardware attestation. Implementations can provide TPM, SGX, TrustZone, or
/// other attestation mechanisms. The default implementation below is a
/// non-failing stub that returns a deterministic "simulated" attestation.

pub type AttestationResult = HashMap<String, Value>;

pub trait HardwareTrust {
    /// Produce an attestation payload as JSON-like map. Implementations should
    /// include measured boot hashes, PCR values, or other evidence.
    fn attest(&self) -> Result<AttestationResult, String>;

    /// Query a short human-friendly description of the hardware trust backend.
    fn backend_description(&self) -> String;
}

/// A stub implementation that returns deterministic placeholder values.
pub struct HardwareTrustStub;

impl HardwareTrust for HardwareTrustStub {
    fn attest(&self) -> Result<AttestationResult, String> {
        let mut m = AttestationResult::new();
        // Deterministic demo values — NOT real attestation.
        m.insert("backend".to_string(), Value::String("stub".to_string()));
        m.insert("timestamp".to_string(), Value::String("1970-01-01T00:00:00Z".to_string()));
        m.insert("pcr_0".to_string(), Value::String("sha256:0000000000000000000000000000000000000000000000000000000000000000".to_string()));
        m.insert("note".to_string(), Value::String("This is a simulated attestation for demo purposes.".to_string()));
        Ok(m)
    }

    fn backend_description(&self) -> String {
        "stub (no real hardware attestation)".to_string()
    }
}

/// Helper: try to run a short external command and capture output, used by some
/// platform adapters.
pub(crate) fn run_command_output(cmd: &str, args: &[&str]) -> Result<String, String> {
    let output = Command::new(cmd).args(args).output().map_err(|e| format!("failed to spawn {}: {}", cmd, e))?;
    if !output.status.success() {
        return Err(format!("command {} failed: {}", cmd, output.status));
    }
    String::from_utf8(output.stdout).map_err(|e| format!("invalid utf8 output: {}", e))
}
