# Z-12: Sovereign Runtime Security Platform

> **Deterministic verification. Hardened execution. Continuous compliance. Runtime enforcement.**

---

## Why Z-12 Exists

Modern software systems increasingly rely on autonomous services, AI agents, automation pipelines, and distributed infrastructure to make decisions in real time. As these systems become more capable, the consequences of executing unverified actions become significantly greater.

Traditional security solutions often focus on observing events after they occur or responding once an incident has already happened. Z-12 approaches the problem differently: instead of assuming execution should proceed unless something appears suspicious, Z-12 establishes multiple layers of verification before, during, and after runtime.

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

## Enforcement flow

```text
Pike sensor ─▶ runtime event ─▶ ACM decision ─▶ ACM_DENY ─▶ Kill Vector ─▶ SIGKILL + forensic log
```

`handle_acm_decision()` in `src/sensors/pike_reaper/reaper/src/main.c` is the
concrete integration point (tested via `make test_killswitch`).

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
