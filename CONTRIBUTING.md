# Contributing to EVK

Thanks for your interest in contributing.

## Prerequisites

- A recent stable Rust toolchain (install via [rustup](https://rustup.rs)).

## Build, test, and quality gates

Before opening a pull request, make sure all of the following pass locally — CI runs
exactly these:

```bash
cargo build --release --locked --verbose
cargo test  --release --locked --verbose -- --nocapture
cargo fmt --all --check
cargo clippy --all-targets --all-features -- -D warnings
```

## Guidelines

- Keep changes focused and minimal.
- Add or update tests for any behavior change. The `.evkp` round-trip is covered by
  `tests/evkp_verify.rs` (self-contained, generates bundles at runtime) and
  `tests/comprehensive.rs` (26 integration tests).
- Run `cargo fmt` before committing; do not introduce new `clippy` warnings.
- Do not commit build artifacts (`/target`) or secrets.
- Keep `Cargo.lock` committed so builds stay reproducible.

## Commit / PR

- Use clear, descriptive commit messages.
- Describe *what* changed and *why* in the pull request.
