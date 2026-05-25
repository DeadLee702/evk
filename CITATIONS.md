# Citations and Tools

## Software Dependencies
- **Rust 1.78+**: Deterministic bytecode generation.
- **sha2 crate**: SHA-256 implementation (FIPS 180-4).
- **zip crate**: ZIP file reading/writing.
- **clap**: CLI parsing.
- **anyhow**: Error handling.

## Security Standards
- **FIPS 180-4**: SHA-256 specification.
- **ZIP File Format**: PKWARE specification.

## No External AI/LLM Dependencies
EVK core logic contains no prompt-based guardrails or LLM calls. All verification logic is static, compiled Rust bytecode.
