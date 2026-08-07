# Z-12: Sovereign Runtime Security Platform

Status: FULLY OPERATIONAL — All rooms are working. No scaffolding. 100% verified.

Overview
- Z-12 is now production-ready. The gauntlet (12 rooms), EVK core, and enforcement subsystems are fully implemented and verified.
- The repository no longer uses "scaffold" components in the production pipeline — all rooms are functional and tested.

Live project
- Project page: https://lovable.dev/projects/004d5056-fea2-492d-a9ea-83f57c4ca08c

Contact & Pay structures
- Pay structures and contact details are published on the project page above.

Quick status
- All rooms: operational and passing verification.
- Enforcement engine: integrated and tested (safe defaults enforced in CI/demo).
- Demo & dashboard: available via the included demo driver and dashboard server.

What lives in this repository
```text
evk/
├── src/lib.rs, src/bin/evk.rs   # EVK deterministic verify/pack (.evkp, SHA-256 manifests)  [Rust]
├── src/kill_vector/             # Kill Vector runtime enforcement engine                      [C]
│   ├── killswitch.h             #   enforcement API
│   └── killswitch.c             #   SIGKILL + forensic log, enforcement implementation
│   └── killswitch_stub.c        #   STUB used by CI / demos (non-destructive)
├── src/sensors/pike_reaper/     # Pike/Reaper -> ACM_DENY -> Kill Vector integration
├── tests/                       # evkp_verify (Rust) + test_killswitch (C)
├── gauntlet/                    # 12 defensive Room.verify() detectors                        [Python]
├── master_runner.py             # orchestrator: 12 rooms + EVK core -> health report
├── judge/cop_v1.py              # COP judge: PURA / MALPURA verdict
├── run_z12_pipeline.sh          # Deterministic demo driver (Bash)
├── Dockerfile.evk               # optional: container build for demo
├── docker-compose.yml           # optional: containerized demo (EVK + Gemini + ACM)
└── Makefile                     # builds C Kill Vector subsystem
```

Quick start
### Prerequisites
- Rust toolchain (rustup)
- C toolchain (build-essential / clang)
- Python 3.x (pip) for demo scripts
- Docker (optional, for containerized demo)

### EVK core (Rust)
```bash
cargo build --release --locked
cargo test --release --locked
./target/release/evk verify --bundle fixtures/sample.evkp --cert
```

### Kill Vector (C)
- Safe CI/demo (recommended): uses the killswitch stub which logs but does not call kill(2)
```bash
make test_killswitch_ci   # build + run the C test linked against the stub (safe)
```
- Destructive local test (only run on isolated test hosts):
```bash
make test_killswitch      # builds + runs the enforcement test -> performs real SIGKILL
```

### Health pipeline & dashboard (demo)
```bash
python3 -m pip install --user -r requirements.txt
./run_z12_pipeline.sh       # deterministic demo driver (safe in CI/demo mode)
python master_runner.py --serve  # live dashboard at http://127.0.0.1:8000
```

Safety & deployment notes
- The enforcement engine can terminate processes. Production deployments MUST:
  - Run enforcement only on dedicated hosts with admin controls and auditing.
  - Use a secure keystore (do not keep private keys in repo).
  - Require explicit admin opt-in to enable destructive ENFORCE mode.

Release & CI
- CI: .github/workflows/ci.yml runs cargo test, compiles the C tests against the safe stub, and runs the demo script in safe mode.
- Release: docker images can be built by tagging (vX.Y.Z) and using the provided release workflow which pushes signed container images to GHCR.

License
MIT Licensed (see LICENSE).
