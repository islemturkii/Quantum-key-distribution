"""
bb84_protocol.py — Full BB84 QKD Protocol Pipeline
====================================================
Alice → (quantum channel + Eve) → Bob
Then: sifting → error analysis → reconciliation → privacy amplification → AES-CTR
"""
import numpy as np
from src.bit_generator import generate_bits
from src.basis_generator import generate_bases
from src.eve_attack import intercept_resend_attack
from src.noise import apply_channel_noise
from src.measurement import measure_bits
from src.sifting import sift_key
from src.error_analysis import calculate_error_rate
from src.information_reconciliation import reconcile_keys
from src.privacy_amplification import privacy_amplification, estimate_eve_information
from src.hybrid_encryption import run_hybrid_demo

# ---------- Security threshold (BB84 theoretical: 11%) ----------
QBER_THRESHOLD = 0.11


def run_bb84(
    n_bits: int = 256,
    noise_rate: float = 0.0,
    eve_interception_rate: float = 0.0,
    message: str = "Hello, Quantum World!",
    verbose: bool = True,
) -> dict:
    """
    Run a complete BB84 QKD session and return a structured result dict.

    Parameters
    ----------
    n_bits               : number of qubits Alice sends
    noise_rate           : channel noise probability per bit
    eve_interception_rate: fraction of qubits Eve intercepts (0–1)
    message              : plaintext to encrypt with the derived AES key
    verbose              : print step-by-step trace
    """

    def log(msg):
        if verbose:
            print(msg)

    log("=" * 60)
    log("  BB84 Quantum Key Distribution Protocol")
    log("=" * 60)

    # ── Step 1: Alice generates bits & bases ──────────────────────
    log(f"\n[Step 1] Alice generates {n_bits} random bits and bases")
    alice_bits  = generate_bits(n_bits)
    alice_bases = generate_bases(n_bits)
    log(f"  Alice bits  (first 10): {[int(x) for x in alice_bits[:10]]}")
    log(f"  Alice bases (first 10): {alice_bases[:10].tolist()} (0=+, 1=×)")

    # ── Step 2: Eve intercepts (optional) ─────────────────────────
    log(f"\n[Step 2] Eve intercepts at rate {eve_interception_rate:.0%}")
    transmitted_bits, eve_bases = intercept_resend_attack(
        alice_bits, alice_bases, interception_rate=eve_interception_rate
    )
    eve_active = eve_interception_rate > 0
    log(f"  Eve active: {eve_active}")

    # ── Step 3: Channel noise ─────────────────────────────────────
    log(f"\n[Step 3] Apply channel noise ({noise_rate:.0%})")
    noisy_bits = apply_channel_noise(transmitted_bits, noise_rate=noise_rate)

    # ── Step 4: Bob chooses bases & measures ──────────────────────
    log("\n[Step 4] Bob chooses random bases and measures")
    bob_bases   = generate_bases(n_bits)
    bob_results = measure_bits(noisy_bits, alice_bases, bob_bases)

    # ── Step 5: Sifting ───────────────────────────────────────────
    log("\n[Step 5] Key sifting — keep only matching-basis positions")
    alice_sifted, bob_sifted, matching = sift_key(
        alice_bits, alice_bases, bob_bases, bob_results
    )
    sifted_len = len(alice_sifted)
    log(f"  Sifted key length: {sifted_len} bits  ({sifted_len/n_bits:.0%} of original)")

    # ── Step 6: QBER estimation ───────────────────────────────────
    log("\n[Step 6] QBER estimation")
    qber, mismatches = calculate_error_rate(alice_sifted, bob_sifted)
    log(f"  QBER = {qber:.4f}  ({mismatches} errors in {sifted_len} bits)")
    log(f"  Security threshold: {QBER_THRESHOLD}")
    secure = qber <= QBER_THRESHOLD
    log(f"  Channel status: {'✓ SECURE' if secure else '✗ EAVESDROPPING DETECTED — ABORT'}")

    # ── Step 7: Information reconciliation ───────────────────────
    log("\n[Step 7] Information reconciliation (CASCADE-inspired, 5 passes)")
    alice_rec, bob_rec, corrections = reconcile_keys(alice_sifted, bob_sifted)
    qber_after, _ = calculate_error_rate(alice_rec, bob_rec)
    log(f"  Corrections applied: {corrections}")
    log(f"  QBER after reconciliation: {qber_after:.6f}")

    # ── Step 8: Privacy amplification ────────────────────────────
    log("\n[Step 8] Privacy amplification (SHA-256 → 128-bit AES key)")
    eve_info = estimate_eve_information(qber, sifted_len)
    log(f"  Estimated Eve's info: {eve_info:.1f} bits")
    alice_key = privacy_amplification(alice_rec)
    bob_key   = privacy_amplification(bob_rec)
    log(f"  Alice key: {alice_key.hex()}")
    log(f"  Bob   key: {bob_key.hex()}")
    log(f"  Keys match: {alice_key == bob_key}")

    # ── Step 9: Hybrid AES-CTR encryption ────────────────────────
    log(f"\n[Step 9] Hybrid AES-CTR encryption of message: '{message}'")
    hybrid = run_hybrid_demo(alice_key, bob_key, message)
    log(f"  Ciphertext (hex): {hybrid['ciphertext_hex']}")
    log(f"  Decryption success: {hybrid['decryption_success']}")
    if hybrid['decryption_success']:
        log(f"  Recovered message : '{hybrid['decrypted_message']}'")

    log("\n" + "=" * 60)

    return {
        "n_bits": n_bits,
        "noise_rate": noise_rate,
        "eve_interception_rate": eve_interception_rate,
        "sifted_length": sifted_len,
        "qber": round(qber, 6),
        "qber_after_reconciliation": round(qber_after, 6),
        "corrections": corrections,
        "secure": secure,
        "eve_info_bits": round(eve_info, 2),
        "alice_key_hex": alice_key.hex(),
        "bob_key_hex": bob_key.hex(),
        "keys_match": alice_key == bob_key,
        "message": message,
        "ciphertext_hex": hybrid["ciphertext_hex"],
        "decryption_success": hybrid["decryption_success"],
        "decrypted_message": hybrid.get("decrypted_message"),
    }


if __name__ == "__main__":
    print("\n── Scenario A: No noise, no Eve ──")
    run_bb84(n_bits=512, noise_rate=0.0, eve_interception_rate=0.0)

    print("\n── Scenario B: Noise only (5%) ──")
    run_bb84(n_bits=512, noise_rate=0.05, eve_interception_rate=0.0)

    print("\n── Scenario C: Full Eve intercept ──")
    run_bb84(n_bits=512, noise_rate=0.0, eve_interception_rate=1.0)

    print("\n── Scenario D: Partial Eve (25%) + some noise ──")
    run_bb84(n_bits=512, noise_rate=0.02, eve_interception_rate=0.25)
