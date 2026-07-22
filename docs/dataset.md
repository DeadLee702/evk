# Dataset Documentation

## Test Fixtures Overview

All test fixtures are synthetically generated to represent real-world forensic artifacts. Each `.evkp` file contains binary evidence with an embedded 2-byte status code that indicates the type of incident.

### Fixture Generation

Tests generate `.evkp` bundles at runtime in a temp directory.
See `tests/comprehensive.rs` and `tests/evkp_verify.rs` for `evk pack` usage.
The only committed fixture required is `fixtures/nist-m57.json`.

### Test Dataset Composition

| Fixture | Status Code | Incident Type | Source | Purpose |
|---------|------------|---------------|--------|---------|
| incident_7f3a.evkp | 0x0F2E | Handoff Conflict | Synthetic | Step executed by wrong actor |
| incident_12b9.evkp | 0x0E1A | Race Condition | Synthetic | Concurrent modification detected |
| incident_3c8d.evkp | 0x0D44 | Orphaned Step | Synthetic | Step with no parent process |
| incident_5e41.evkp | 0x1A4F | Transaction Replay | Synthetic | Re-execution of prior transaction |
| incident_6a2f.evkp | 0x1B88 | Schema Mutation | Synthetic | Unexpected data structure change |
| incident_8b7c.evkp | 0x1C2B | Log Truncation | Synthetic | Critical log entries removed |
| incident_9d1e.evkp | 0x2A90 | Packet Modification | Synthetic | In-transit data tampering |
| incident_a4f2.evkp | 0x2B11 | Timestamp Drift | Synthetic | Significant clock skew |
| incident_b5c3.evkp | 0x2C7F | API Spoofing | Synthetic | Impersonated service endpoint |
| incident_c6d9.evkp | 0x3A01 | Prompt Injection | Synthetic | Malicious input to LLM/system |
| incident_d7e5.evkp | 0x3B99 | Entropy Leakage | Synthetic | Cryptographic material exposed |
| incident_e8a1.evkp | 0x3C4D | Register Forgery | Synthetic | Tampered hardware/software register |
| incident_clean.evkp | 0x0000 | Clean (Valid) | Synthetic | Baseline: no incidents detected |

### Data Format

Each `.evkp` file is a binary artifact with:
- **Bytes 0-1**: 2-byte big-endian status code (identifies incident type)
- **Bytes 2+**: Synthetic forensic evidence payload

### Test Coverage

**Platform Coverage**: 
- ubuntu-latest (Linux x86_64)
- macos-latest (macOS ARM64)
- Byte-identical hashes across both platforms prove reproducibility

**Reproducibility Proof**:
- SHA256 hash remains identical across all CI runs
- Green CI badge on both platforms = auditor-verified evidence integrity

## Running Tests

```bash
# Build the project
cargo build --release

# Run all tests
cargo test --release -- --nocapture

# Verify a bundle
./target/release/evk verify --bundle runtime_test.evkp
```

## What Each Test Validates

1. **Incident Detection**: Each `.evkp` file is correctly classified to its incident type
2. **Clean Baseline**: The clean anchor file returns VALID (0x0000)
3. **Binary Fidelity**: Artifacts are byte-identical across platforms
4. **Hash Reproducibility**: SHA256 hashes never diverge between runs
5. **Evidence Integrity**: No mutations occur between collection and classification

## Next Steps: Real SIFT Data

Current fixtures are synthetic for fast testing (< 1 second). Future:
- Real disk images from SIFT case library
- Memory dumps from live incident response scenarios
- Network packet captures with embedded artifacts
- Expand to 50+ test cases for comprehensive coverage
