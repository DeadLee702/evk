# Z-12: Sovereign Runtime Security Platform

> **Deterministic verification. Hardened execution. Continuous compliance. Runtime enforcement.**

---

## Why Z-12 Exists

Modern software systems increasingly rely on autonomous services, AI agents, automation pipelines, and distributed infrastructure to make decisions in real time. As these systems become more capable they also expand the attack surface, and traditional reactive security approaches are no longer sufficient.

Traditional security solutions often focus on observing events after they occur or responding once an incident has already happened. Z-12 approaches the problem differently: instead of assuming execution is trustworthy, we verify and enforce trust before and during runtime.

**Verify trust before execution. Continuously validate runtime behavior. Enforce policy when required.**

---

## Ecosystem

| Repository | Purpose |
|------------|---------|
| **EVK** (this repo) | Deterministic identity and integrity verification **+ Kill Vector runtime enforcement** |
| **[Gemini-Box](https://github.com/DeadLee702/gemini-box)** | Hardened execution environment (ed25519 signing) |
| **[Adversarial Compliance Matrix](https://github.com/DeadLee702/adversarial-compliance-matrix)** | Continuous runtime validation |
| **Z-12 Dashboard** (`dashboard/`) | Unified operational visibility |

Each layer performs one responsibility while contributing to the overall runtime security posture.

---

## What lives in this repository

```text
evk/
├── src/lib.rs, src/bin/evk.rs   # EVK deterministic verify/pack (.evkp, SHA-256 manifests)  [Rust]
├── src/kill_vector/             # Kill Vector runtime enforcement engine                      [C]
│   ├── killswitch.h             #   enforcement API
│   └── killswitch.c             #   SIGKILL + forensic log, unsafe-PID guard
├── src/sensors/pike_reaper/     # Pike/Reaper -> ACM_DENY -> Kill Vector integration (scaffold) [C]
├── tests/                       # evkp_verify (Rust) + test_killswitch (C)
├── gauntlet/                    # 12 defensive Room.verify() detectors                        [Python]
├── master_runner.py            # orchestrator: 12 rooms + EVK core -> health report
├── judge/cop_v1.py             # COP judge: PURA / MALPURA verdict
├── mha_run.sh                  # pipeline driver (exit 0=PURA, 1=MALPURA, 2=critical)
├── dashboard/index.html        # React/Tailwind control plane (reads /api/health)
├── z12                        # Python integration CLI (integration-only orchestrator)
├── run_z12_pipeline.sh        # Deterministic demo driver (Bash)
└── Makefile                    # builds the C Kill Vector subsystem
```

---

## Quick start

### EVK core (Rust)
```bash
cargo build --release --locked
cargo test  --release --locked -- --nocapture
./target/release/evk verify --bundle fixtures/sample.evkp --cert
```

### Kill Vector (C)
```bash
make test_killswitch     # builds + runs the enforcement test -> "Kill Vector Test: PASS"
make reaper              # builds the Pike/Reaper integration scaffold
```

The Kill Vector terminates a policy-denied process (`kill(pid, SIGKILL)`), refuses
unsafe PIDs (`pid <= 1`), and appends a forensic record to `/var/log/z12/kill.log`
(override with `Z12_KILL_LOG`) in the form:

```text
[1720000000] PID=4521 REASON=POLUITA_LINEAGE ACTION=SIGKILL
```

### Health pipeline + dashboard
```bash
pip install -r requirements.txt
./mha_run.sh                                  # build -> gauntlet -> judge -> verdict
python master_runner.py --serve               # live dashboard at http://127.0.0.1:8000
```

---

## Z-12 Integration & Demo (z12)

We provide a lightweight orchestration layer and deterministic demo runner that builds and exercises the full Z-12 platform (EVK, Gemini-Box, Adversarial Compliance Matrix) and produces machine- and human-readable reports.

Files added for integration:
- `z12` — Python orchestration CLI (integration-only). Usage: `./z12 demo` (requires python3).
- `run_z12_pipeline.sh` — Deterministic Bash demo driver. Usage: `./run_z12_pipeline.sh`.

Quick demo (sibling repo layout)
1. Ensure the three repositories are siblings:
   - `../evk`
   - `../gemini-box`
   - `../adversarial-compliance-matrix`
2. Make scripts executable:
   - `chmod +x ./z12 ./run_z12_pipeline.sh`
3. Run a deterministic demo against the fixture `test/incident_7f3a.evkp`:
   - `./run_z12_pipeline.sh`
   - or `./z12 demo`
4. Outputs:
   - `z12_demo_report.json` / `z12_demo_report.html` / `z12_demo_evidence.html` (printable)

Environment overrides (if repos are not siblings):
- `Z12_EVK_PATH` — path to EVK
- `Z12_GEMINI_PATH` — path to Gemini-Box
- `Z12_ACM_PATH` — path to Adversarial Compliance Matrix
- `FIXTURE_PATH` — override fixture location

Safety: the Kill Vector runtime enforces SIGKILL for denied processes. Running the enforcement test (`make test_killswitch`) requires a C toolchain and should be executed only on isolated test hosts (`./run_z12_pipeline.sh --run-kill-vector-test`).

---

## Dashboard API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Full health report (12-room gauntlet + EVK core status) |
| `GET /api/swarm` | Swarm report (per-room status, attack vectors, zodiac mapping) |
| `GET /api/version` | Platform version + component versions |
| `GET /api/reports` | Forensic reports (non-PURA incidents with enforcement actions) |

---

## Enforcement flow

```text
Pike sensor ─▶ runtime event ─▶ ACM decision ─▶ ACM_DENY ─▶ Kill Vector ─▶ SIGKILL + forensic log
```

`handle_acm_decision()` in `src/sensors/pike_reaper/reaper/src/main.c` is the
concrete integration point (tested via `make test_killswitch`).

---

## Hackathon demo (judge-friendly)

Problem: autonomous systems lack deterministic runtime integrity and enforcement.

Solution: Z-12 unifies deterministic verification (EVK), hardened signing/triage (Gemini-Box), and a compliance verdict engine (ACM) with deterministic, auditable evidence and enforcement.

How to demo (60–90 seconds):
- Run `./run_z12_pipeline.sh` (or `./z12 demo`).
- Open `z12_demo_report.html` and `z12_demo_evidence.html` in a browser — these are demo‑ready artefacts you can hand to judges.
- Point judges to the `summary` block in the JSON report (`z12_demo_report.json`) for machine-verifiable proof.

Judges quick checklist:
- [ ] Clone the three repositories as siblings (evk, gemini-box, adversarial-compliance-matrix)
- [ ] Ensure Rust toolchain and Python3 are installed
- [ ] `chmod +x ./run_z12_pipeline.sh` then `./run_z12_pipeline.sh`
- [ ] Open `z12_demo_report.html` and `z12_demo_evidence.html` to inspect results

---

## Core principles
1. **Deterministic verification** — verify identity/integrity before execution.
2. **Layered security** — each component owns one responsibility.
3. **Runtime enforcement** — detection *plus* enforcement provides control.
4. **Observable operations** — the platform always reports its current state.
5. **Modular architecture** — components evolve independently.

## Health states
| State | Meaning |
|---|---|
| **PURA** | Healthy |
| **VIGLA** | Warning |
| **POLUITA** | Compromised |

---

## Honesty notes
- The Kill Vector engine and its test are **real and working**. The Pike/Reaper
  sensor and the ACM transport are **scaffolds** — no live event source is wired.
- Gauntlet rooms are rule-based **demonstrations**; no detection-accuracy benchmarks
  are claimed. **Ghost Matrix** is a containment *concept*, not yet an implemented service.

MIT licensed (see `LICENSE`).

---

## Production Readiness

Z-12 is containerized and release-ready with safe defaults. The Kill Vector runs in
**STUB** mode by default in CI and demo containers — it logs enforcement decisions
without calling `kill(2)`. Real enforcement (`ENFORCE`) is opt-in and requires a
dedicated host with admin consent.

### Containerized demo

```bash
cp .env.example .env          # KILL_MODE=STUB by default
docker build -f Dockerfile.evk -t evk:local .
docker run --rm -p 8000:8000 evk:local ./run_z12_pipeline.sh
# or full multi-service demo:
docker-compose up --build
```

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KILL_MODE` | `STUB` | `STUB` logs only; `ENFORCE` performs real `kill(2)` |
| `Z12_KILL_LOG` | `/var/log/z12/kill.log` | Forensic enforcement log path |
| `GEMINI_KEY_PATH` | `$HOME/.z12/keystore/gemini_ed25519` | ed25519 private key location |
| `DOCKER_REGISTRY` | `ghcr.io` | Container registry for releases |
| `DOCKER_NAMESPACE` | `your-org-or-user` | Registry namespace |

### Key management

```bash
./scripts/generate_ed25519_keys.sh    # generates ed25519 keypair locally
```

Keys are never stored in the repository. For production, use HashiCorp Vault, a
cloud KMS, or an HSM (PKCS#11). See `.env.example` for path configuration.

### CI & releases

- Tagged releases (`v1.0.0`) trigger the [release workflow](.github/workflows/release.yml)
  which builds and publishes container images to GitHub Container Registry (GHCR).
- CI runs `cargo fmt --check`, `cargo clippy -D warnings`, `cargo audit`, `cargo test`,
  and the C Kill Vector test suite on every push and pull request.

### Kubernetes deployment

```bash
kubectl apply -f deploy/evk-deployment.yaml
```

The manifest defaults to `KILL_MODE=STUB`. To enable enforcement, set the env var
to `ENFORCE` and deploy on a dedicated, privileged node with RBAC controls.

### Production checklist

1. **Safety** — STUB mode everywhere by default; ENFORCE is opt-in on dedicated hosts.
2. **Key management** — external keystore (Vault/HSM/KMS); never commit keys.
3. **CI** — fmt, clippy, audit, unit + integration tests in containers.
4. **Releases** — signed container images via GHCR on tagged releases.
5. **Observability** — structured JSON logs + forensic audit trail.
6. **Security review** — third-party audit required before production deployment.
