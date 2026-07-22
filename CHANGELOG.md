# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Committed `Cargo.lock` for reproducible, `--locked` builds.
- `.gitignore` for build artifacts and Python caches.
- Unit tests for the `evk_lib` Merkle `Node` (`get_hash`, `find_mismatch`).
- Missing project docs: `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`,
  `ROADMAP.md`, `MASTER_MANIFEST.md`.
- CI `fmt` + `clippy` quality gate.

### Changed
- `evk pack` now reads the `--job`, `--snapshot`, and `--input` files, adds them to the
  bundle, and writes a `manifest.json` with per-file SHA-256 hashes and a `manifest_hash`.
- `evk verify` now validates an `.evkp` bundle end-to-end (manifest hash, per-file
  hashes, ordering) and exits non-zero on any mismatch; added `--bundle`/`--cert` flags.
- Renamed the binary from `evk-cli` to `evk` to match documentation.
- Moved the GitHub Actions workflow from `github/workflows/evk.yml` to
  `.github/workflows/ci.yml` (the previous path was never triggered) and modernized it
  (checkout@v4, `dtolnay/rust-toolchain`, cargo cache, `--locked`).
- Rewrote `ARCHITECTURE.md` to match the actual CLI, binary name, and bundle format.
- Removed committed `.evkp` fixtures. Tests now generate bundles at runtime.
- `evkp_verify` test rewritten to be self-contained (no fixture dependency).

### Fixed
- Cleared `cargo fmt` and `cargo clippy -D warnings` failures.
- Removed unused-variable warnings in `src/lib.rs` and `src/bin/evk.rs`.
- Fixed CI by pointing tests to `target/release/evk` binary.

## [1.0.0]

- Initial EVK prototype: SHA-256 manifest concept and CLI skeleton.
