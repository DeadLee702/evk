# Achieving Deterministic Integrity: Reproducible Evidence Bundles with the EVK Stack

### Abstract
Modern CI/CD guarantees tests pass. It does not guarantee artifacts are identical. ZIP compression, file order, and timestamps create byte-level drift. Same source + same compiler ≠ same artifact. For audits, compliance, and incident response, "close enough" fails.

The **EVK Stack** solves this with the `.evkp` specification: a deterministic bundle format using canonical JSON, sorted file order, and SHA-256 verification. Result: byte-for-byte reproducible, tamper-evident artifacts and 1-line verification. Same input → same hash, every time, on every machine.

**Core Repositories:**
- [evk](https://github.com/DeadLee702/evk) — Deterministic packer and verifier
- [gemini-box](https://github.com/DeadLee702/gemini-box) — Cryptographic signing layer (ed25519) *(planned, not yet integrated)*
- [adversarial-compliance-matrix](https://github.com/DeadLee702/adversarial-compliance-matrix) — Red-team failure mode simulation *(planned, not yet integrated)*

### 1. Executive Summary
*The pain:* You ship `v1.2.3` to production. Months later an auditor asks: "Prove this exact bundle ran in prod." CI logs are gone. Rebuild produces a different hash. You're now explaining timestamps and compression levels instead of delivering proof.

*The antidote:* The EVK Stack enforces deterministic primitives:
1. **Deterministic Bundling** (`evk`): Canonical manifest, sorted order, STORE-mode ZIP.
2. **Cryptographic Signing** (`gemini-box`): ed25519 signatures for non-repudiation *(roadmap)*.
3. **Adversarial Validation** (`adversarial-compliance-matrix`): Test against realistic attack/failure scenarios *(roadmap)*.

*Outcome:* Auditors verify with confidence. Engineers ship with proof. Compliance teams get tamper-evident, reproducible evidence bundles without heavy infrastructure.

### 2. The Challenge: The Reproducibility Gap
CI/CD pipelines give green checkmarks but not identical artifacts.

**Three core problems:**
1. **Timestamp drift** — Standard tools embed `mtime`.
2. **Order variance** — Filesystem readdir is non-deterministic across OSes.
3. **Compression variance** — Different deflate levels produce different bytes.

Even with reproducible builds, the final distribution package often breaks determinism. This creates audit nightmares in regulated industries.

The EVK Stack closes the gap at the artifact level.

### 3. The Methodology: Deterministic Primitives + Layered Defense
The stack follows strict rules for `VALID` / `INVALID` outcomes only.

**EVK Bundle Flow:**
```
Developer
    ↓
EVK Packer (evk)
    ↓ (sort paths → hash files → canonical JSON manifest)
ZIP Writer (STORE mode, fixed order)
    ↓
.evkp bundle
```

**Key Properties:**
- Manifest uses sorted keys, no whitespace drift.
- File order is canonical.
- Verification is fail-closed.
- `SOURCE_DATE_EPOCH` overrides the `created` timestamp for full reproducibility.

### 4. Case Study: Affidavit of Build
**Scenario:** Production bundle `app_v1.2.3.evkp` deployed Jan 12, 2026. Auditor requests proof eight months later.

**Verification (one command):**
```bash
./target/release/evk verify --bundle app_v1.2.3.evkp --cert
```

**Result:**
```
{
  "bundle": "app_v1.2.3.evkp",
  "files_verified": 3,
  "manifest_hash": "sha256:...",
  "status": "VALID"
}
CERT: sha256:... VALID 3 files verified at 2026-...
```

No CI logs or build servers required. The bundle itself carries the proof.

**Business Value:**
- Audit latency drops from weeks to minutes.
- Strong defense in regulated environments (finance, healthcare, government).
- Tamper-evident chain of custody.

### 5. Architecture Overview
- **evk** (this repo): Core library and CLI for packing/verifying `.evkp` files. Includes a Merkle-style `Node` type for tamper localization and a Kill Vector runtime enforcement engine (C).
- **gemini-box**: Adds ed25519 signing for authenticity *(roadmap)*.
- **adversarial-compliance-matrix**: Simulates real-world failures *(roadmap)*.

### 6. Conclusion & Call to Action
The EVK Stack turns "trust me" into verifiable math. Deterministic bundles deliver reproducible, auditable artifacts that stand the test of time.

**For Auditors & Compliance:** Run the verifier. Get `VALID` or `INVALID`.
**For Engineers:** Ship with proof built in.
**For Security Teams:** Test resilience with the adversarial matrix *(roadmap)*.

**Get Started:**
1. Clone: `git clone https://github.com/DeadLee702/evk`
2. Build: `cargo build --release --locked`
3. Verify: `./target/release/evk verify --bundle fixtures/sample.evkp --cert`

*Open Source core available under MIT.*

---
_EVK Stack — Verifies file integrity. Same bytes in = same verifiable outcome. © 2026 DeadLee702_
