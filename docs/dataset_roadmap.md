# Dataset Roadmap: Synthetic → Real SIFT

## Current State: Synthetic Validation ✅

**Status**: 12/12 incidents detected on synthetic test fixtures
- All incidents properly classified
- Zero false positives/negatives
- 100% reproducible across platforms (ubuntu-latest + macos-latest)
- Green CI badge = auditable proof

**Limitation**: Synthetic data is generated. Real forensic evidence is messier.

---

## Phase 2: Real SIFT Integration (In Progress)

### Why Real Data Matters

Synthetic proves the pipeline works. Real SIFT proves it matters in the field.

### Target Datasets

**1. NIST CFReDS (M57 Case)**
- **Source**: http://www.cfreds.nist.gov/
- **Status**: Public domain, no privacy issues
- **Content**: Real laptop forensic image (labeled incidents)
- **Format**: `.E01` (Encase), `.dd` (raw)
- **Download**: ~500MB, includes incident metadata

**2. Digital Corpora GovDocs1**
- **Source**: http://digitalcorpora.org/
- **Status**: Real-world government documents + filesystem artifacts
- **Use case**: Test packet modification, log truncation detection
- **Format**: Raw disk images, filesystem dumps

**3. GCFA Training Images**
- **Source**: SANS Institute (public training datasets)
- **Status**: Labeled with known incidents
- **Use case**: Validate against real forensic training benchmarks

### Legal/Privacy Considerations

✅ **What we're using:**
- NIST CFReDS (public domain)
- Digital Corpora (licensed for research/testing)
- GCFA public training sets (educational use)

❌ **What we're NOT using:**
- Customer production disks
- PII-containing images
- Proprietary incident response data

All sources are cited in dataset.md and documentation.

---

## Phase 2 Implementation Plan

### Step 1: E01 Ingestion (gemini-box)

Add libewf-based reader to extract artifacts from Encase images:

```rust
// gemini-box/src/readers/e01.rs
pub struct E01Reader {
    handle: *mut libewf_handle_t,
}

impl E01Reader {
    pub fn open(path: &str) -> Result<Self> {
        // Use libewf to open .E01 file
        // Extract filesystem artifacts
        // Output same format as synthetic tests
    }
}
```

**Input**: `.E01` Encase image (NIST M57)
**Output**: Standardized artifact bundles (same format as synthetic)
**Result**: evk + classifier unchanged, just different input

### Step 2: Canonical Test Case

Add real NIST M57 subset to test fixtures:

```
tests/fixtures/nist_m57_sample.bin  (extracted from CFReDS, labeled)
tests/fixtures/m57_metadata.json    (incident types, expected outputs)
```

Run verification:
```bash
cargo test --release -- nist_m57
```

### Step 3: Re-validate Accuracy

Update accuracy report with real data results:

| Dataset | Cases | Detected | False Pos | Notes |
|---------|-------|----------|-----------|-------|
| Synthetic | 13 | 13 | 0 | 100% baseline |
| NIST M57 Subset | TBD | TBD | TBD | Real forensic validation |
| Digital Corpora | TBD | TBD | TBD | Filesystem patterns |

**Honest reporting**: If we hit 9/12 on M57, we report 9/12 + explain why.

---

## Expected Outcomes

### If Real Data Validates Well (9-12/12)
- ✅ Proves system works on actual forensic evidence
- ✅ Enterprise credibility (not just synthetic)
- ✅ Roadmap becomes track record

### If Real Data Shows Gaps (< 8/12)
- ✅ Still valuable: "Here's where the classifier needs improvement"
- ✅ Shows honest evaluation
- ✅ Identifies real-world edge cases

Either way, you move from "synthetic proof" → "real-world validation."

---

## Timeline

- **Week 1**: Download NIST CFReDS M57, build E01 reader
- **Week 2**: Extract test fixtures, validate pipeline
- **Week 3**: Re-run accuracy report, update documentation
- **Week 4**: Publish results on GitHub

---

## Why This Matters for Judges (Post-Hackathon)

When you update your Devpost + GitHub with real SIFT results:
- "Synthetic: 12/12" → proof of concept ✅
- "NIST M57: 10/12" → production readiness ✅
- "Digital Corpora: 9/12" → real-world validation ✅

That's the story arc: Idea → Proof → Enterprise credibility.

---

## Resources

- **NIST CFReDS**: http://www.cfreds.nist.gov/
- **Digital Corpora**: http://digitalcorpora.org/
- **libewf (E01 reader)**: https://github.com/libyal/libewf
- **Rust libewf binding**: https://crates.io/crates/libewf-rs

---

## Next Steps

1. Download NIST M57 case (~500MB)
2. Build E01 reader in gemini-box
3. Extract real artifacts
4. Re-run evk + classifier
5. Update accuracy report with real data
6. Publish results
