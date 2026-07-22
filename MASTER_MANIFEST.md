# Master Manifest

An index of the EVK repository and what each part is for.

## Rust crate (`evk-lib` / binary `evk`)

| Path | Purpose |
|------|---------|
| `Cargo.toml` | Crate manifest: library `evk_lib` + binary `evk`. |
| `Cargo.lock` | Pinned dependency graph for reproducible `--locked` builds. |
| `src/lib.rs` | Merkle-style `Node` (`Leaf`/`Internal`) with `get_hash`, `internal_hash`, `find_mismatch`; unit tested. |
| `src/bin/evk.rs` | CLI: `pack` (build an `.evkp` bundle) and `verify` (validate a bundle). |
| `tests/comprehensive.rs` | 26 integration tests: Merkle tree edge cases, CLI pack/verify round-trip, tamper detection, determinism, manifest validation. |
| `tests/evkp_verify.rs` | Self-contained integration test that packs and verifies a bundle at runtime. |
| `tests/test_killswitch.c` | Kill Vector enforcement test (C). |
| `fixtures/sample.evkp` | Prebuilt bundle used by the README quick-start example. |

## C subsystem (Kill Vector)

| Path | Purpose |
|------|---------|
| `src/kill_vector/killswitch.h` | Enforcement API header. |
| `src/kill_vector/killswitch.c` | SIGKILL + forensic log, unsafe-PID guard. |
| `src/sensors/pike_reaper/reaper/src/main.c` | Pike/Reaper -> ACM_DENY -> Kill Vector integration scaffold. |
| `Makefile` | Builds the C Kill Vector subsystem. |

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
| `WHITEPAPER.md` | Project write-up. |
| `TRY-IT-OUT.md` | Quick-start guide. |
| `CITATIONS.md` | Citations. |

## CI/CD

| Path | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Build + test (Linux/macOS) and fmt + clippy gates. |

## Python "gauntlet" harness (experimental, not part of the Rust build)

| Path | Purpose |
|------|---------|
| `gauntlet/`, `gauntlet.yml` | 12 "zodiac room" attack-scenario detectors (`Room.verify`). |
| `scripts/validate_gauntlet.py` | Gauntlet spec validator. |
| `master_runner.py` | Orchestrator: 12 rooms + EVK core -> health report; optional FastAPI dashboard server. |
| `dashboard/index.html` | Static dashboard UI (React/Tailwind, reads `/api/health`). |
| `requirements.txt` | Python deps (`fastapi`, `uvicorn`). |
| `mha_run.sh` | Pipeline driver (exit 0=PURA, 1=MALPURA, 2=critical). |
| `judge/cop_v1.py` | COP judge: PURA / MALPURA verdict. |

> Note: the Python gauntlet harness is experimental and independent of the Rust crate.
> It is not invoked by CI. The gauntlet rooms are rule-based demonstrations; no
> detection-accuracy benchmarks are claimed.
