# evk 

## 🏆 FIND EVIL! Hackathon Submission

**[View Full Submission on Devpost →](https://devpost.com/software/gemini-box-m0kxy1)**

Part of the 3-layer incident detection stack for Protocol SIFT. Multi-Agent Framework entry with 12/12 tests passing.

## Pipeline Status
![CI Status](https://github.com/DeadLee702/evk/actions/workflows/evk.yml/badge.svg?branch=main)
This project uses an automated cross-platform CI/CD pipeline to ensure bundle integrity. Every commit is validated across Linux and macOS environments to prevent architectural regressions.

## 📚 Documentation

- **[Architecture](docs/architecture.md)** — 3-layer stack diagram + security boundaries
- **[Accuracy Report](docs/accuracy.md)** — 13/13 tests passing (100%)
- **[Dataset Documentation](docs/dataset.md)** — Test fixtures and sources
- **[Agent Execution Logs](docs/logs.md)** — Full CI traces and traceability
- **[Devpost Description](devpost.md)** — Complete project submission text

## Usage

### Pack a bundle:
```bash
./target/release/evk pack --job tests/job.evk --snapshot tests/snapshot.evk --input tests/input.bin --output bundle.evkp
```

### Verify a bundle:
```bash
./target/release/evk verify bundle.evkp
```

Expected output on clean artifact:
```
VALID (0x0000) - Clean artifact
```

Expected output on incident:
```
INVALID (0x0F2E) - Handoff conflict detected
```

## Related Projects

This is part of a three-layer deterministic verification stack:
- **[evk](https://github.com/DeadLee702/evk)** ← You are here (Bundle validation & determinism)
- **[gemini-box](https://github.com/DeadLee702/gemini-box)** (Cryptographic signing & verification)
- **[adversarial-compliance-matrix](https://github.com/DeadLee702/adversarial-compliance-matrix)** (12 incident detection)

## License

MIT License - See LICENSE file for details
