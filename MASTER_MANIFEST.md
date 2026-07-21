# Master Manifest

An index of the EVK repository and what each part is for.

## Rust crate (`evk-lib` / binary `evk`)

| Path | Purpose |
|------|---------|
| `Cargo.toml` | Crate manifest: library `evk_lib` + binary `evk`. |
| `Cargo.lock` | Pinned dependency graph for reproducible `--locked` builds. |
| `src/lib.rs` | Merkle-style `Node` (`Leaf`/`Internal`) with `get_hash`, `internal_hash`, `find_mismatch`; unit tested. |
| `src/bin/evk.rs` | CLI: `pack` (build an `.evkp` bundle) and `verify` (validate a bundle). |
| `tests/evkp_verify.rs` | Integration test that verifies `fixtures/sample.evkp`. |
| `tests/job.evk`, `tests/snapshot.evk`, `tests/input.bin` | Sample evidence inputs. |
| `tests/expected_cert.txt` | Reference certificate text. |
| `fixtures/sample.evkp` | Prebuilt bundle used by the integration test. |
| `fixtures/nist-m57.json` | Sample dataset reference. |

## Documentation

| Path | Purpose |
|------|---------|
| `README.md` | Z-12 platform overview (EVK is one component). |
| `ARCHITECTURE.md` | EVK design, `.evkp` bundle format, and CLI usage. |
| `SECURITY.md` | Security policy and reporting. |
| `CONTRIBUTING.md` | Build/test/quality gates and contribution guidelines. |
| `CHANGELOG.md` | Notable changes. |
| `ROADMAP.md` | Planned direction. |
| `LICENSE` | MIT license. |
| `MASTER_MANIFEST.md` | This file. |
| `docs/` | Supplementary notes (architecture, accuracy, dataset, logs). |
| `ACCURACY.md`, `DATASET.md`, `LOGS.md`, `CITATIONS.md`, `WHITEPAPER.md`, `TRY-IT-OUT.md`, `devpost.md` | Project write-ups / hackathon material. |

## CI/CD

| Path | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Build + test (Linux/macOS) and fmt + clippy gates. |

## Python "gauntlet" harness (experimental, not part of the Rust build)

| Path | Purpose |
|------|---------|
| `gauntlet/`, `gauntlet.yml` | 12 "zodiac room" attack-scenario stubs (`Room.verify`). |
| `scripts/validate_gauntlet.py` | Gauntlet spec validator. |
| `master_runner.py` | FastAPI server serving the dashboard + room health. |
| `dashboard/index.html` | Static dashboard UI. |
| `requirements.txt` | Python deps (`fastapi`, `uvicorn`). |
| `mha_run.sh`, `gauntlet.yml` | Gauntlet runner / spec. |

> Note: the Python gauntlet harness is experimental and independent of the Rust crate.
> `master_runner.py` currently references room modules by names that differ from the
> files under `gauntlet/rooms/`, and the rooms expose `verify()` rather than the
> `scan()` it calls; it is left as-is pending a decision on the intended interface.
