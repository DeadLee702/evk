# EVK Verification Report

**Repository:** https://github.com/DeadLee702/evk
**Commit audited:** `6bc538d` (branch `main`)
**Date:** 2026-07-17
**Mode:** Read-only audit. No source files were modified. Only this report was created.

## Legend

- **VERIFIED** — Checked and confirmed working / present / correct.
- **FAILED** — Checked and confirmed broken / incorrect / non-compliant.
- **NOT VERIFIED** — Could not be confirmed (missing input, unverifiable claim, or out of scope for this environment).

## Environment note (affects reproducibility)

The repository pins **no toolchain** (`rust-toolchain.toml` absent) and commits **no `Cargo.lock`**.
The environment's default compiler (`rustc 1.83.0`) **cannot resolve the dependency graph**: with no lock file, Cargo selects the newest compatible transitive crates (e.g. `time-core 0.1.9`) which require the unstable `edition2024` feature and fail to parse under 1.83.

```
error: failed to parse manifest at .../time-core-0.1.9/Cargo.toml
Caused by: feature `edition2024` is required ... not stabilized in this version of Cargo (1.83.0)
```

To evaluate the code at all, the toolchain was upgraded to **`rustc 1.97.1`**. All build/test/quality results below were produced with 1.97.1 unless stated otherwise. This lack of pinning is itself a reproducibility defect (see Dependencies).

---

## 1. REPOSITORY

| Check | Status | Finding |
|-------|--------|---------|
| Directory structure | VERIFIED | Rust crate (`src/lib.rs`, `src/bin/evk.rs`, `tests/`) coexists with an unrelated Python "gauntlet" harness (`gauntlet/`, `master_runner.py`, `scripts/`), a static `dashboard/index.html`, `fixtures/`, and many top-level `.md` files. Mixed-language layout, no clear separation. |
| `Cargo.toml` | VERIFIED (parses) | Valid manifest. Package `evk-lib` v1.0.0, edition 2021, lib `evk_lib`, bin `evk-cli`. Deps: `sha2`, `clap`, `anyhow`, `serde_json`, `chrono`, `zip`. |
| `Cargo.lock` | FAILED | **Not present and not tracked in git.** Breaks `--locked`, breaks reproducible builds, and lets transitive deps float to versions incompatible with the toolchain (see Environment note). |
| Module organization | FAILED | The library (`evk_lib`) is **not referenced by the binary or any test** (`grep evk_lib src/ tests/` → none). The two Rust units are effectively disconnected. |
| Duplicate files | FAILED | Documentation is duplicated across the root and `docs/` with **divergent** content: `ARCHITECTURE.md`↔`docs/architecture.md`, `ACCURACY.md`↔`docs/accuracy.md`, `DATASET.md`↔`docs/dataset.md`, `LOGS.md`↔`docs/logs.md` (all differ, not identical copies). |
| Duplicate modules | FAILED | `master_runner.py` imports modules that **do not exist** (`gauntlet.taurus`, `gauntlet.gemini`, `gauntlet.cancer`, …). Actual room modules live at `gauntlet/rooms/<name>.py` with Esperanto names (`alighostest`, `bridge`, …). The names in `gauntlet.yml`/`rooms/` and the names in `master_runner.py` are two different, conflicting sets. |
| Duplicate functions | VERIFIED (present) | SHA-256 hashing logic is re-implemented in three places independently: `src/lib.rs::get_hash`, `src/bin/evk.rs` (`Sha256::digest`), and `tests/evkp_verify.rs`. No shared helper. |
| Duplicate logic | VERIFIED (present) | Same manifest/hash verification concept described differently in `ARCHITECTURE.md`, `docs/architecture.md`, and the test — none share code. |
| Dead code | FAILED | Entire Merkle-tree library (`Node`, `get_hash`, `find_mismatch`) in `src/lib.rs` is unused. `find_mismatch`'s `Leaf` arm is a no-op that always returns `None` (the `data` field is unused — compiler warning). In `src/bin/evk.rs` the `Pack` command binds `input` but never reads it. |
| Unused code | FAILED | Confirmed by compiler warnings: `unused variable: data` (`src/lib.rs:25`), `unused variable: input` (`src/bin/evk.rs:56`). The whole `evk_lib` crate is unreferenced. |

---

## 2. BUILD

### Command requested: `cargo build --release --locked --verbose`

| Item | Status | Detail |
|------|--------|--------|
| Result (as-specified, `--locked`) | **FAILED** | `error: the lock file .../Cargo.lock needs to be updated but --locked was passed to prevent this`. Fails on a fresh clone because no `Cargo.lock` is committed. Exit code 101. |
| Result (default toolchain 1.83, no lock) | **FAILED** | Dependency resolution pulls `edition2024`-only crates that 1.83 cannot parse (see Environment note). Exit code 101. |
| Result (`cargo build --release --verbose`, rustc 1.97.1) | **VERIFIED** | `Finished \`release\` profile [optimized]`. Exit code 0. Compiles once the toolchain is new enough and a lock is generated. |
| Warnings | **FAILED (2 warnings)** | `unused variable: data` — `src/lib.rs:25`. `unused variable: input` — `src/bin/evk.rs:56`. |
| Errors | VERIFIED (none, 1.97.1) | No compile errors under 1.97.1 once buildable. |

**Net:** The build **as literally requested (`--locked`) FAILS**. It only succeeds with a newer toolchain and after Cargo generates a lock file.

---

## 3. TESTS

### Command requested: `cargo test --release --locked --verbose -- --nocapture`

(Ran successfully only after a `Cargo.lock` was generated by a prior build and with rustc 1.97.1.)

| Item | Status | Detail |
|------|--------|--------|
| Every test executes | **FAILED** | Not all tests execute. The single integration test is `#[ignore]`d and never runs. |
| Passing tests | VERIFIED | 0 passed. |
| Failing tests | VERIFIED | 0 failed. |
| Ignored tests | **FAILED** | 1 ignored: `evkp_verify_manifest_and_hashes` — `ignored, Requires fixtures/sample.evkp to be present`. The required fixture **`fixtures/sample.evkp` is missing** (only `fixtures/nist-m57.json` exists), so the test can never run as shipped. |
| Missing coverage | **FAILED** | Effective coverage ≈ **zero**: `evk_lib` unit tests = 0; `evk-cli` unit tests = 0; doc-tests = 0; the only integration test is permanently ignored. Neither `Verify`/`Pack` CLI paths nor any `Node`/`find_mismatch` logic is exercised. |

Test tallies observed:
```
evk_lib:        0 passed; 0 failed; 0 ignored
evk-cli:        0 passed; 0 failed; 0 ignored
evkp_verify:    0 passed; 0 failed; 1 ignored
Doc-tests:      0 passed; 0 failed; 0 ignored
```

---

## 4. QUALITY

| Check | Status | Detail |
|-------|--------|--------|
| `cargo fmt --check` | **FAILED** | Non-conforming formatting; large diff reported (import ordering, brace/trailing-comma style, trailing whitespace in `src/bin/evk.rs` and others). Exit code 1. |
| `cargo clippy --all-targets --all-features -- -D warnings` | **FAILED** | Fails to compile under `-D warnings`: `error: unused variable: data` (`src/lib.rs:25`) → `could not compile evk-lib (lib)` and `(lib test)`. Exit code 101. |

---

## 5. DEPENDENCIES

| Check | Status | Detail |
|-------|--------|--------|
| Unused dependencies | VERIFIED | All six declared crates are referenced: `sha2`, `clap`, `anyhow`, `serde_json`, `chrono`, `zip` (checked against `src/`). Note: `chrono` is used for timestamps, which **contradicts** `ARCHITECTURE.md`'s "no timestamps" guardrail. |
| Duplicate dependencies | VERIFIED | `cargo tree -d` reports **no** duplicate crate versions in the resolved graph. |
| Vulnerable dependencies | VERIFIED (with caveat) | `cargo audit` (advisory DB, 1166 advisories, 102 crates) reported **no vulnerabilities** for the resolved graph. **Caveat:** this was run against a freshly-generated lock, not a committed one — because no `Cargo.lock` is pinned, a future resolution could differ and this result is not reproducible. |
| Version conflicts | VERIFIED | No unresolved conflicts once built with 1.97.1. However `--locked` is unusable (no committed lock), and the graph is **not resolvable at all** under the repo's implied/default toolchain (1.83) — a de-facto toolchain/version conflict. |

---

## 6. SECURITY

| Check | Status | Detail |
|-------|--------|--------|
| Hardcoded secrets | VERIFIED (none) | No real secrets in source. Grep matches occur only in the gauntlet **detector** code (`gauntlet/rooms/alighostest.py`, `gauntlet.yml`) and in local build artifacts under `target/`. |
| Exposed keys | VERIFIED (none) | No private keys / API tokens / AWS keys found in tracked files. |
| Unsafe defaults | **FAILED** | `Verify` computes a hash and **always** emits `"status": "verified"` — it never compares against any expected/known value, so it verifies nothing. `Pack` writes `metadata.json` (docs/tests expect `manifest.json`) and **ignores the `--input` file entirely**, producing a bundle with no evidence. `zip` uses `FileOptions::default()` (store, no integrity beyond zip CRC). |
| Input validation | **FAILED** | Essentially none. `Verify` reads any path and reports success regardless of content. `Pack` accepts `--job`/`--snapshot`/`--input` but validates nothing and drops `--input`. No path/size/format checks. |
| Panic paths | VERIFIED (src) / FAILED (tests) | No `unwrap`/`expect`/`panic!`/`unreachable!` in `src/` (errors are `Result`-propagated). The test file (`tests/evkp_verify.rs`) uses 5 `unwrap()`/`as_*().unwrap()` calls that will panic on malformed manifests — acceptable in tests but brittle. No `unsafe` blocks anywhere. |

---

## 7. DOCUMENTATION

### Presence

| File | Status |
|------|--------|
| `README.md` | VERIFIED (present) |
| `LICENSE` | VERIFIED (present — MIT, © 2026 DeadLee702) |
| `SECURITY.md` | **FAILED (missing)** |
| `CONTRIBUTING.md` | **FAILED (missing)** |
| `CHANGELOG.md` | **FAILED (missing)** |
| `ROADMAP.md` | **FAILED (missing)** |
| `ARCHITECTURE.md` | VERIFIED (present) |
| `MASTER_MANIFEST.md` | **FAILED (missing)** |

### Accuracy

| Claim / Doc | Status | Detail |
|-------------|--------|--------|
| Project identity | **FAILED** | `README.md` calls the project "**Z-12: Sovereign Runtime Security Platform**" (EVK is one of five sub-repos); `ARCHITECTURE.md` calls it "**EVK: Evidence Verification Kit**"; `docs/architecture.md` describes a "**3-Layer Incident Detection Stack**". Three inconsistent framings. |
| `ARCHITECTURE.md` run commands | **FAILED** | Documents `./target/release/evk pack …` and `evk verify --bundle incident.evkp --cert`. Actual binary is **`evk-cli`** (not `evk`); `Verify` takes a **positional** file argument, not `--bundle`, and there is **no `--cert` flag**. Commands as written will not work. |
| "No timestamps" guardrail (`ARCHITECTURE.md`) | **FAILED** | Contradicted by the code, which stamps `Utc::now()` in both `Verify` output and the `Pack` metadata. |
| `docs/architecture.md` ed25519 / VALID-INVALID claims | **FAILED** | Claims ed25519 signatures and VALID/INVALID cryptographic verdicts. No ed25519 dependency or code exists; `Verify` never returns INVALID. |
| `ACCURACY.md` "1000/1000 detected, 0 false positives" | **NOT VERIFIED** | No test, dataset, or harness in the repo reproduces this claim. |
| `mha_run.sh` "ALL ROOMS: PASS" | **NOT VERIFIED** | Script `echo`s hardcoded PASS output and `exit 0`; it runs nothing. |

---

## 8. CI/CD

| Check | Status | Detail |
|-------|--------|--------|
| GitHub Actions present/active | **FAILED** | The workflow is at **`github/workflows/evk.yml`**, not **`.github/workflows/`**. GitHub only reads workflows under the dotted `.github/` path, so **this workflow never runs**. No `.github/` directory exists. |
| Workflow validity | VERIFIED (YAML parses) | The YAML itself is structurally valid (`name: CI`, push/PR on `main`, matrix `ubuntu-latest`/`macos-latest`). But it uses the **deprecated/archived** `actions-rs/toolchain@v1` and outdated `actions/checkout@v3`. |
| Build pipeline | **FAILED** | Even if relocated, the build step runs `cargo build --release --verbose` **without `--locked`** and with no committed `Cargo.lock`, so it is not reproducible; and `toolchain: stable` would face the same edition2024 resolution risk on older runners. |
| Test pipeline | **FAILED** | Runs `cargo test --verbose`; the only test is `#[ignore]`d and its fixture is missing, so CI would exercise **no** tests. No `fmt`/`clippy`/`audit` gates. |

---

## Summary of findings

| # | Area | Status |
|---|------|--------|
| Build `--locked` (as requested) | BUILD | **FAILED** (no `Cargo.lock`) |
| Build (newer toolchain, no lock) | BUILD | VERIFIED (2 warnings) |
| Tests execute | TESTS | **FAILED** (1 ignored, fixture missing, ~0 coverage) |
| `cargo fmt --check` | QUALITY | **FAILED** |
| `cargo clippy -D warnings` | QUALITY | **FAILED** |
| Unused / duplicate / vuln / conflict deps | DEPENDENCIES | Mostly VERIFIED; **no committed lock** = reproducibility FAILED |
| Secrets / keys / panics(src) / unsafe | SECURITY | VERIFIED (clean) |
| Unsafe defaults / input validation | SECURITY | **FAILED** |
| Required docs presence | DOCUMENTATION | **FAILED** (5 of 8 missing) |
| Docs accuracy | DOCUMENTATION | **FAILED** (multiple contradictions) |
| GitHub Actions | CI/CD | **FAILED** (wrong path — never triggers) |
| Dead code / duplication / module wiring | REPOSITORY | **FAILED** |

### Highest-impact issues

1. **No `Cargo.lock` committed** → the requested `--locked` build fails and builds are non-reproducible.
2. **CI never runs** — workflow is under `github/workflows/` instead of `.github/workflows/`.
3. **No effective test coverage** — the single test is ignored and its fixture (`fixtures/sample.evkp`) is missing.
4. **`Verify` verifies nothing** and **`Pack` ignores its input** — the core tool does not do what the docs claim.
5. **`fmt` and `clippy -D warnings` both fail**, and the library is entirely dead code.
6. **Documentation is internally contradictory** and 5 of the 8 required docs are missing.
