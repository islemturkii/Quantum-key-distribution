# CR-5: Quantum-Based Cryptographic Mechanisms — BB84 QKD Simulator

> **Course**: CyberSec Lab I — 2025/26 Spring  
> **Topic**: CR-5 — Quantum-based crypto mechanisms complementary to classical protocols  
> **Focus**: Quantum Key Distribution (QKD), BB84 protocol, eavesdropping detection, hybrid encryption

---

## Project Overview

This project implements a **complete, simulation-based BB84 Quantum Key Distribution (QKD) pipeline** in Python. It demonstrates how quantum cryptography can be used as a complementary mechanism to classical cryptographic protocols.

The simulator covers the full QKD lifecycle:

```
Alice → Quantum Channel → (Eve?) → Bob
  ↓                                 ↓
Basis announcement (public channel)
  ↓                                 ↓
        Key Sifting
              ↓
        QBER Estimation  ← Security decision
              ↓
   Information Reconciliation (CASCADE)
              ↓
    Privacy Amplification (SHA-256)
              ↓
     Hybrid AES-CTR Encryption
```

---

## Project Structure

```
qkd_project/
├── main.py                          # Entry point — run everything from here
├── evaluate.py                      # Full evaluation + figure generation
├── requirements.txt
├── README.md
│
├── src/                             # Core BB84 modules
│   ├── __init__.py
│   ├── bb84_protocol.py             # Full pipeline orchestrator
│   ├── bit_generator.py             # Alice's random bit generation
│   ├── basis_generator.py           # Random basis selection (+/×)
│   ├── eve_attack.py                # Intercept-resend attack simulation
│   ├── noise.py                     # Quantum channel noise model
│   ├── measurement.py               # Bob's quantum measurement
│   ├── sifting.py                   # Key sifting (basis reconciliation)
│   ├── error_analysis.py            # QBER calculation
│   ├── information_reconciliation.py # CASCADE-inspired reconciliation
│   ├── privacy_amplification.py     # SHA-256 privacy amplification
│   ├── hybrid_encryption.py         # AES-CTR hybrid encryption
│   ├── visualization.py             # Basic plotting
│   └── advanced_visualization.py    # Advanced multi-parameter plots
│
├── demo/
│   └── interactive_demo.py          # Live colour terminal demo
│
├── tests/
│   └── test_bb84.py                 # 25 unit tests (all passing)
│
└── results/
    ├── evaluation_results.csv       # Raw evaluation data (25 combos × 20 trials)
    └── figures/
        ├── qber_vs_interception.png
        ├── acceptance_vs_interception.png
        ├── qber_heatmap.png
        ├── bb84_error_comparison.png
        ├── bb84_full_comparison.png
        └── reconciliation_effectiveness.png
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install numpy matplotlib cryptography
```

### 2. Run the interactive demo (for the defense!)
```bash
python3 main.py demo
```
Select a scenario from the menu. Shows every protocol step with colour output.

### 3. Run all scenarios non-interactively
```bash
python3 main.py quick
```

### 4. Run the full evaluation (regenerates all figures)
```bash
python3 main.py evaluate
```

### 5. Run the test suite
```bash
python3 main.py test
```

---

## Module Descriptions

### `src/bit_generator.py`
Generates Alice's random binary bit sequence using `numpy.random.randint`.
- `generate_bits(n)` → `np.ndarray` of 0s and 1s

### `src/basis_generator.py`
Generates random BB84 bases: `0 = rectilinear (+)`, `1 = diagonal (×)`.
- `generate_bases(n)` → `np.ndarray`
- `format_bases(bases)` → `list[str]` of `+`, `×`, `-`

### `src/eve_attack.py`
Simulates Eve's **intercept-resend attack**. Eve picks a random basis for each intercepted qubit. If her basis matches Alice's she gets the bit for free; otherwise she introduces errors.
- `intercept_resend_attack(alice_bits, alice_bases, interception_rate)`

### `src/noise.py`
Models quantum channel imperfections as random bit flips with probability `noise_rate`.
- `apply_channel_noise(bits, noise_rate)`

### `src/measurement.py`
Bob measures qubits in his random basis. If his basis matches, he gets the correct bit. If not, the result is random.
- `measure_bits(transmitted_bits, transmitted_bases, bob_bases)`

### `src/sifting.py`
Alice and Bob publicly compare bases (not bits) and keep only matching positions.
- `sift_key(alice_bits, alice_bases, bob_bases, bob_results)` → ~50% of bits retained

### `src/error_analysis.py`
Computes **QBER = mismatches / sifted_length**. QBER > 11% → abort session.
- `calculate_error_rate(alice_key, bob_key)` → `(qber, mismatches)`

### `src/information_reconciliation.py`
Multi-pass **CASCADE-inspired** reconciliation. 5 passes with block sizes `[4, 8, 4, 8, 16]`, random permutations on passes 2–5, and a final single-bit sweep.
- `reconcile_keys(alice_key, bob_key)` → `(alice_final, bob_corrected, corrections)`

### `src/privacy_amplification.py`
Hashes the reconciled key with **SHA-256** and truncates to 128 bits to eliminate any information Eve may have learned.
- `privacy_amplification(key)` → `bytes` (16 bytes = 128-bit AES key)
- `estimate_eve_information(qber, sifted_length)` → estimated bits leaked

### `src/hybrid_encryption.py`
Uses the QKD-derived key for **AES-CTR mode encryption** — the classical complement.
- `encrypt_message(key, plaintext)` → `(nonce, ciphertext)`
- `decrypt_message(key, nonce, ciphertext)` → `str`
- `run_hybrid_demo(alice_key, bob_key, message)` → result dict

---

## Key Results

### QBER vs Eve Interception Rate
Eve's intercept-resend attack causes QBER to rise approximately **linearly** with interception rate. At 100% interception, QBER ≈ 25% (well above the 11% threshold).

| Eve Rate | QBER (no noise) | Accepted? |
|----------|----------------|-----------|
| 0%       | 0.000          | ✓ Always  |
| 25%      | ~0.062         | ✓ Usually |
| 50%      | ~0.129         | ✗ Rarely  |
| 75%      | ~0.190         | ✗ Never   |
| 100%     | ~0.250         | ✗ Never   |

### Security Threshold
- **BB84 theoretical threshold**: 11% QBER
- Above this, the session is **aborted** — no key is used
- Under real noise (≤ 5%), keys remain usable with low Eve activity

### Key Acceptance Rate
With zero noise and no Eve: **100% acceptance**. With 10% noise and any Eve: sessions are almost always aborted, correctly detecting the threat.

---

## Physics Background

BB84 relies on the **no-cloning theorem** and **Heisenberg's uncertainty principle**:
- An eavesdropper **cannot copy** an unknown quantum state without disturbing it
- Measuring in the wrong basis **collapses** the quantum state, introducing detectable errors
- Alice and Bob can detect Eve's presence by observing elevated QBER

The two conjugate bases used:
- **Rectilinear (+)**: |0⟩ = horizontal, |1⟩ = vertical
- **Diagonal (×)**: |0⟩ = 45°, |1⟩ = 135°

---

## Future Work
- Implement entanglement-based **E91 protocol** (Ekert 1991)
- Add **decoy state** QKD to counter photon-number-splitting attacks
- Integrate with a real QKD hardware SDK (e.g., ID Quantique Clavis)
- Implement **continuous-variable QKD (CV-QKD)**
- Build a network-layer simulation with multiple QKD nodes

---

## References
1. Bennett, C.H. & Brassard, G. (1984). "Quantum cryptography: Public key distribution and coin tossing."
2. Gisin, N. et al. (2002). "Quantum cryptography." *Reviews of Modern Physics*.
3. ETSI GS QKD 014 V1.1.1 (2019). "Quantum Key Distribution — Protocol and Data Format."
4. Lo, H.K. & Chau, H.F. (1999). "Unconditional security of quantum key distribution over arbitrarily long distances." *Science*.
5. Brassard, G. et al. (1994). "Secret-key reconciliation by public discussion." *Lecture Notes in Computer Science*.
