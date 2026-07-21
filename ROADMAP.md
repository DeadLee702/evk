# Roadmap

Planned direction for EVK. Items are indicative, not commitments.

## Near term
- [ ] Cryptographic signing of bundles (e.g. ed25519) for authenticity, not just integrity.
- [ ] Streaming hashing for large evidence files.
- [ ] Richer `verify` output (per-file status table, machine-readable exit summary).

## Mid term
- [ ] Deterministic, canonical manifest serialization independent of the JSON library.
- [ ] Optional detached manifest / signature files.
- [ ] `cargo audit` gate in CI.

## Long term
- [ ] Integration with the wider Z-12 platform components described in the README.
- [ ] Published, versioned `.evkp` format specification.
