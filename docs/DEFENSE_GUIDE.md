# Defense Day Guide — CR-5 QKD Project
## Mini-Conference, June 15 · 9:00 AM · Room 2.218

---

## What to Show (25-minute structure)

### 1. Motivation & Problem Statement (3 min)
- "Classical cryptography (RSA, ECC) is threatened by quantum computers via Shor's algorithm."
- "We need quantum-safe alternatives. QKD offers *information-theoretic* security."
- "This project implements and evaluates BB84 — the foundational QKD protocol."

### 2. Background / Related Work (4 min)
- Explain BB84 physics: superposition, no-cloning theorem, uncertainty principle
- Mention existing QKD products: ID Quantique Clavis, Toshiba QKD, OpenQKD
- ETSI QKD standards (GS QKD 014)

### 3. Our Contribution (2 min)
- Complete BB84 simulation with all post-processing stages
- Systematic evaluation across 25 parameter combinations (noise × Eve)
- Integration with AES-CTR hybrid encryption

### 4. Protocol Walk-through (3 min)
Show the diagram:  Alice → Eve? → Bob → Sifting → QBER → Reconcile → Amplify → AES

### 5. LIVE DEMO — Run this command (5 min):
```bash
cd qkd_project
python3 main.py demo
```
- Select **Option 1** (Ideal) → show QBER=0, keys match, decryption works
- Select **Option 3** (Full Eve) → show QBER~0.25, "EAVESDROPPING DETECTED", session aborted
- Select **Option 4** (Partial Eve) → borderline case, discuss threshold

### 6. Results & Evaluation (4 min)
Open the figures in `results/figures/`:
1. **qber_vs_interception.png** — "QBER rises linearly with Eve's interception rate"
2. **acceptance_vs_interception.png** — "Security mechanism correctly rejects sessions"
3. **qber_heatmap.png** — "Combined noise+Eve effect — security boundary visible"
4. **reconciliation_effectiveness.png** — "CASCADE corrects errors without revealing key bits"
5. **bb84_full_comparison.png** — "4-scenario summary"

### 7. Future Work (2 min)
- E91 (entanglement-based) protocol
- Decoy state QKD (photon-number-splitting attack resistance)
- Real hardware integration
- CV-QKD

### 8. Q&A (2 min buffer)

---

## Quick Commands for Demo Day

```bash
# From the project root:
python3 main.py demo          # Interactive demo (for live defense)
python3 main.py quick         # All 4 scenarios automated
python3 main.py test          # Show 25/25 tests passing
python3 main.py evaluate      # Regenerate all figures if needed
```

---

## Common Questions & Answers

**Q: What is QBER?**
A: Quantum Bit Error Rate — the fraction of sifted bits that Alice and Bob disagree on.
Ideal channel: 0%. Full Eve: ~25%. Our threshold: 11%.

**Q: Why 11% as the threshold?**
A: Theoretical BB84 security proof. Above 11%, Eve could have enough information
to break the key even after privacy amplification. The 11% comes from the
information-theoretic analysis by Shor & Preskill (2000).

**Q: What does Eve's intercept-resend attack actually do?**
A: Eve intercepts each qubit, measures it in a random basis, then resends it.
If she chose the same basis as Alice: she learns the bit and Bob gets the right answer.
If different basis: she introduces a 50% error chance and gets a random result herself.
Result: 25% error rate at 100% interception (since ~50% of bases won't match).

**Q: Why is QBER ~25% and not 50% under full Eve?**
A: Eve only disturbs bits where she chose the wrong basis AND Alice and Bob chose matching bases.
Probability: 50% (wrong basis) × 50% (bit wrong given wrong basis) = 25%.

**Q: What is privacy amplification?**
A: A hash function (SHA-256 here) that compresses the reconciled key to eliminate
any information Eve may have leaked. The output key is shorter but provably secret.

**Q: Why AES after all this quantum work?**
A: QKD solves the key distribution problem. Once Alice and Bob share a secret key,
they use classical symmetric encryption (AES) for actual data — this is the 'hybrid' approach.
QKD complements classical crypto, it does not replace it.

**Q: What hardware does real QKD use?**
A: Single-photon sources and detectors. Fiber-optic channels for metropolitan networks
(~100 km), or free-space/satellite for longer distances (China's Micius satellite achieved 7,600 km).

**Q: Is your implementation truly quantum?**
A: No — it is a classical simulation of the quantum protocol. The random choices
faithfully model quantum measurement outcomes (basis collapse, 50% probability when
bases differ). Real quantum effects require photonic hardware.

---

## Setup Instructions (for someone who has never seen the project)

### Requirements
- Python 3.9+
- No special quantum hardware needed

### Install
```bash
pip install numpy matplotlib cryptography
```

### Run
```bash
# 1. Go to the project folder
cd qkd_project

# 2. Run the demo
python3 main.py demo

# 3. Or run quick scenarios
python3 main.py quick

# 4. Or run tests to show correctness
python3 main.py test
```

### If figures need to be regenerated
```bash
python3 main.py evaluate
# Figures appear in results/figures/
```

---

## Grading Self-Assessment

| Criterion | Evidence |
|-----------|----------|
| General progress | All 9 protocol stages implemented and working |
| Theoretical report | README + this guide covers physics, math, and protocol theory |
| Practical results | 25 unit tests pass, 6 evaluation figures, systematic evaluation CSV |
| Code quality | Modular design, type hints, docstrings, error handling |
| Demo | Live interactive terminal demo with 5 scenarios |
