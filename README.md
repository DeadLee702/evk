# evk 

## Pipeline Status
![CI Status](https://github.com/DeadLee702/evk/actions/workflows/evk.yml/badge.svg?branch=main)
This project uses an automated cross-platform CI/CD pipeline to ensure bundle integrity. Every commit is validated across Linux and macOS environments to prevent architectural regressions.

## Usage

### Pack a bundle:
```bash
./target/release/evk pack --job tests/job.evk --snapshot tests/snapshot.evk --input tests/input.bin --output bundle.evkp
Testing current build
 
## Verification Status
✅ **Determinism Verified: 12/12 Adversarial Tests Pass**

See [adversarial-compliance-matrix](https://github.com/DeadLee702/adversarial-compliance-matrix) for the full test suite.

The bundle validator catches:
- Handoff conflicts
- Race conditions
- Schema mutations
- Timestamp drift
- [... all 12 incident types]
