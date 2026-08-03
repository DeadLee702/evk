# Z-12: Sovereign Runtime Security Platform
> Deterministic verification. Hardened execution. Continuous compliance. Runtime enforcement.
---
## Why Z-12 Exists
Modern software systems increasingly rely on autonomous services, AI agents, automation pipelines, and distributed infrastructure to make decisions in real time. Z-12 verifies identity and integrity before execution, continuously validates runtime behavior, and enforces policy when required.
---
## Ecosystem
| Repository | Purpose |
|------------|---------|
| **EVK** (this repo) | Deterministic identity and integrity verification + Kill Vector runtime enforcement |
| **[Gemini-Box](https://github.com/DeadLee702/gemini-box)** | Hardened signing & non-repudiation (ed25519) |
| **[Adversarial Compliance Matrix](https://github.com/DeadLee702/adversarial-compliance-matrix)** | Continuous runtime validation / verdict engine |
| **Z-12 Dashboard** (`dashboard/`) | Unified operational visibility |
Each layer performs one responsibility while contributing to the overall runtime security posture.
---
## What lives in this repository
```text
evk/
├── src/lib.rs, src/bin/evk.rs   # EVK deterministic verify/pack (.evkp, SHA-256 manifests)  [Rust]
├── src/kill_vector/             # Kill Vector runtime enforcement engine                      [C]
│   ├── killswitch.h             #   enforcement API
│   └── killswitch.c             #   SIGKILL + forensic log, unsafe-PID guard (production)
│   └── killswitch_stub.c        #   STUB used by CI / demos (non-destructive)
├── src/sensors/pike_reaper/     # Pike/Reaper -> ACM_DENY -> Kill Vector integration (scaffold) [C]
├── tests/                       # evkp_verify (Rust) + test_killswitch (C)
├── gauntlet/                    # 12 defensive Room.verify() detectors                        [Python]
├── master_runner.py             # orchestrator: 12 rooms + EVK core -> health report
├── judge/cop_v1.py               # COP judge: PURA / MALPURA verdict
├── run_z12_pipeline.sh          # Deterministic demo driver (Bash)
├── Dockerfile.evk               # optional: container build for demo
├── docker-compose.yml           # optional: containerized demo (EVK + Gemini + ACM)
└── Makefile                     # builds C Kill Vector subsystem
```
How it fits together
- EVK verifies deterministic bundles (.evkp) and exposes CLI: `evk verify`.
- The Kill Vector is the enforcement layer: when ACM denies a lineage, EVK/orchestrator calls the Kill Vector to enforce (SIGKILL). The repository provides a safe stub (killswitch_stub.c) used by CI and demos so no host processes are terminated during tests.
- The Python gauntlet + judge + master_runner orchestrate the demo pipeline.
---
## Quick start
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
### Health pipeline + dashboard (demo)
```bash
python3 -m pip install --user -r requirements.txt
./run_z12_pipeline.sh       # deterministic demo driver (safe in CI/demo mode)
python master_runner.py --serve  # live dashboard at http://127.0.0.1:8000
```
---
## Environment / safe defaults (.env / demo)
Create .env (or export env vars) to override defaults. Example (.env.example provided):
- Z12_KILL_LOG — path to kill log (default: /var/log/z12/kill.log)
- KILL_MODE — STUB (default) or ENFORCE (explicitly enable destructive enforcement)
- Z12_GEMINI_PATH, Z12_ACM_PATH — repository paths for sibling demo
Safety defaults:
- KILL_MODE defaults to STUB: the killswitch stub logs enforcement actions but never calls kill(2).
- CI runs `make test_killswitch_ci` and uses the stub.
- To enable actual enforcement you must explicitly set KILL_MODE=ENFORCE on a dedicated, auditable host.
---
## Containerized demo (optional)
We provide Dockerfile.evk and a docker-compose.yml that run EVK + Gemini-Box + ACM together. By default these run in safe STUB mode. To build and run:
```bash
# build locally
docker build -f Dockerfile.evk -t evk:local .
# run safe demo
docker run --rm -e KILL_MODE=STUB -e Z12_KILL_LOG=/tmp/z12_kill.log -v $(pwd)/tmp:/tmp -p 8000:8000 evk:local ./run_z12_pipeline.sh
# or with docker-compose:
cp .env.example .env
docker-compose up --build
```
---
## Dashboard API Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Full health report (12-room gauntlet + EVK core status) |
| `GET /api/swarm` | Swarm report (per-room status, attack vectors, zodiac mapping) |
| `GET /api/version` | Platform component versions |
| `GET /api/reports` | Forensic reports (non-PURA incidents with enforcement actions) |
---
## Integration & demo (z12)
Quick demo (sibling repo layout)
1. Ensure the three repositories are siblings:
   - `../evk`
   - `../gemini-box`
   - `../adversarial-compliance-matrix`
2. Make scripts executable:
   - `chmod +x ./run_z12_pipeline.sh ./z12`
3. Run:
   - `./run_z12_pipeline.sh` or `./z12 demo`
4. Outputs:
   - `z12_demo_report.json`, `z12_demo_report.html`, `z12_demo_evidence.html`
Environment overrides:
- Z12_EVK_PATH, Z12_GEMINI_PATH, Z12_ACM_PATH, FIXTURE_PATH
---
## Release & CI
- CI: .github/workflows/ci.yml runs cargo test, compiles the C tests against the safe stub, and runs the demo script in safe mode.
- Release: docker images can be built by tagging (vX.Y.Z) and using the provided release workflow which pushes signed container images to GHCR.
---
## Safety & productization notes
- The enforcement engine can kill processes. Production deployments MUST:
  - Run enforcement only on dedicated hosts with admin controls and auditing.
  - Use a secure keystore (do not keep private keys in repo).
  - Require explicit admin opt-in to enable ENFORCE mode.
- Add observability (structured logs, metrics) and a documented incident response playbook before using ENFORCE in production.
---
## Honesty notes
- Kill Vector enforcement engine and its test are real. Sensors and ACM transport are scaffolds and require integration work to connect live event sources. Gauntlet rooms are demonstrations, not tuned detection engines.
MIT Licensed (see LICENSE).
