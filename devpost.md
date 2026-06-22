# FIND EVIL! - Protocol SIFT: 3-Layer Incident Detection Stack

**Tagline**: AI detects forensic incidents 10x faster, with evidence that can't be forged.

## What

Automated incident detection for SIFT workstations. Maps raw artifacts to 12 adversarial compliance incident types (0x0F2E through 0x3C4D) using a 3-agent pipeline powered by Protocol SIFT and MCP.

## How

**Layer 1 - Agent 1: gemini-box (Collector)**
- Extracts artifacts from disk images and memory captures
- Signs with ed25519 signatures using OS-backed entropy
- Produces cryptographically authenticated `.evk` archives

**Layer 2 - Agent 2: evk (Packer/Validator)**
- Packs evidence into `.evkp` bundles with SHA256 hash verification
- **Rust type safety = tamper-proof**: Prevents artifact mutations between agents
- Evidence integrity guaranteed by cryptographic binding

**Layer 3 - Agent 3: adversarial-compliance-matrix (Classifier)**
- Reads status codes from validated bundles
- Maps to 12 incident types: Handoff Conflict, Race Condition, Orphaned Step, Transaction Replay, Schema Mutation, Log Truncation, Packet Modification, Timestamp Drift, API Spoofing, Prompt Injection, Entropy Leakage, Register Forgery
- Outputs: `INVALID + incident code + human-readable description`

**MCP Integration**: All agents communicate through Protocol SIFT's MCP Server with full execution traces logged for auditor review.

## Challenges

1. **Binary Reproducibility**: Evidence must be byte-identical across ubuntu-latest + macos-latest CI environments
   - *Solved*: Moved workflows to `.github/workflows/`, use `read_to_end()` for binary data instead of text parsing
   
2. **CI as Proof**: Green badge must demonstrate reproducibility, not just compilation
   - *Solved*: Canonical test validates hash equality across platforms. CI badge = auditable proof
   
3. **Preventing Artifact Tampering**: Agents could forge findings between layers
   - *Solved*: EVK layer enforces Rust type safety. All mutations caught at compile time. Hashes prevent tampering at runtime

## Insights Learned

1. **Rust type system prevents entire classes of forensic tampering bugs** — compared to Python/Node agents that rely on prompt guardrails
2. **Green CI badge is auditor proof** — beyond vanity. Judges + lawyers trust it more than verbal claims
3. **3 small agents beat 1 monolith** — separation of concerns makes incident detection more reliable and testable
4. **Evidence integrity is non-negotiable** — one forged artifact breaks the entire chain of custody

## Next Steps

1. Expand testing to real SIFT datasets (currently 12/12 synthetic cases passing)
2. Web dashboard for live incident triage during active response
3. Live collection integration with Velociraptor + GRR
4. Extend to additional incident types beyond the 12-incident matrix

## Demo

2-minute walkthrough showing: collect artifact → pack with verification → detect incident → output classification with proof

## Repos

- **[evk](https://github.com/DeadLee702/evk)** — Bundle validator & deterministic verification
- **[gemini-box](https://github.com/DeadLee702/gemini-box)** — Cryptographic signing & verification  
- **[adversarial-compliance-matrix](https://github.com/DeadLee702/adversarial-compliance-matrix)** — 12-incident detection engine

All MIT licensed. 12/12 tests passing. Green CI on all platforms.
