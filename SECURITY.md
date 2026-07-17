# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

Please report security issues privately rather than opening a public issue.

- Open a [GitHub security advisory](https://github.com/DeadLee702/evk/security/advisories/new), or
- Contact the maintainer at the address listed on the GitHub profile.

Include a description, reproduction steps, and the affected commit. You can expect an
initial acknowledgement within a few days.

## Scope & Design Notes

EVK verifies the integrity of `.evkp` bundles via SHA-256 hashes:

- Every evidence file is hashed and recorded in `manifest.json`.
- `manifest.json` itself is protected by a `manifest_hash` over its canonical
  (sorted-key) serialization, so the manifest cannot be altered undetected.
- `verify` exits non-zero on any manifest, hash, or ordering mismatch.

SHA-256 provides **integrity**, not **authenticity**: EVK does not currently sign
bundles, so it detects tampering with a known-good manifest but does not by itself
prove *who* produced a bundle. Cryptographic signing is tracked on the roadmap.

No secrets or credentials are stored in this repository.
