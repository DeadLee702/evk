# EVK: Evidence Verification Kit

Byte-level integrity verification for incident response bundles via SHA-256 manifest validation.

## Architecture

**Architectural Guardrails:**
- SHA-256 digest per file before bundling
- Manifest-first read strategy
- Hash verification before file use
- No environment state, no timestamps, no FS enumeration

**No Prompt-based Guardrails.** All logic in Rust bytecode.

## How to Run Locally

### Build
```bash
cargo build --release
./target/release/evk pack --job tests/job.evk --snapshot tests/snapshot.evk --input tests/input.bin --output incident.evkp
./target/release/evk verify --bundle incident.evkp --cert
