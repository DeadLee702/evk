# EVK: Evidence Verification Kit

Byte-level integrity verification for incident-response bundles via SHA-256 manifest validation.

## Architecture

**Design guardrails:**
- SHA-256 digest computed per file before it is bundled.
- Manifest-first read strategy: `manifest.json` is parsed before any evidence file is trusted.
- Every file hash is verified against the manifest before the file is used.
- The `manifest_hash` covers the whole manifest (minus the hash field itself), so the
  manifest cannot be edited without detection.

**Bundle format (`.evkp`)** — a ZIP archive containing:
- the evidence files (added under their base names, e.g. `job.evk`, `snapshot.evk`, `input.bin`);
- `manifest.json`:
  ```json
  {
    "version": "1.0",
    "created": "<RFC3339 timestamp>",
    "files": [ { "path": "job.evk", "hash": "sha256:..." } ],
    "order": [ "job.evk", "snapshot.evk", "input.bin" ],
    "manifest_hash": "sha256:..."
  }
  ```

> Note: bundles embed an RFC3339 `created` timestamp for traceability. Verification is
> otherwise deterministic and depends only on file bytes, not on environment state.

## CLI

The binary is named `evk` (crate `evk-lib`, library `evk_lib`).

### Build
```bash
cargo build --release
```

### Pack
```bash
./target/release/evk pack \
  --job tests/job.evk \
  --snapshot tests/snapshot.evk \
  --input tests/input.bin \
  --output incident.evkp
```

### Verify
```bash
./target/release/evk verify --bundle incident.evkp --cert
```

`verify` prints a JSON report with `"status": "VALID"` on success and exits non-zero
(with an `INVALID: ...` message) if the manifest hash, any file hash, or the ordering
does not check out. The `--cert` flag additionally prints a one-line certificate.

## Library

`src/lib.rs` provides a small Merkle-style `Node` type (`Leaf`/`Internal`) with
`get_hash`, `internal_hash`, and `find_mismatch`, used to locate the path to a tampered
subtree. It is unit-tested in the same file.
