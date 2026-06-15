"""
interactive_demo.py — Live BB84 terminal demo for the mini-conference
=====================================================================
Shows every step of the BB84 protocol in real-time with colour output.
Run:  python3 demo/interactive_demo.py
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from src.bit_generator import generate_bits
from src.basis_generator import generate_bases, format_bases
from src.eve_attack import intercept_resend_attack
from src.noise import apply_channel_noise
from src.measurement import measure_bits
from src.sifting import sift_key
from src.error_analysis import calculate_error_rate
from src.information_reconciliation import reconcile_keys
from src.privacy_amplification import privacy_amplification, estimate_eve_information
from src.hybrid_encryption import run_hybrid_demo

# ANSI colours
R  = "\033[91m"  # red
G  = "\033[92m"  # green
Y  = "\033[93m"  # yellow
B  = "\033[94m"  # blue
M  = "\033[95m"  # magenta
C  = "\033[96m"  # cyan
W  = "\033[97m"  # white
BOLD = "\033[1m"
RESET = "\033[0m"

QBER_THRESHOLD = 0.11
SHOW_BITS = 16   # how many bits to print in traces


def banner(text, color=B):
    width = 60
    print(f"\n{color}{BOLD}{'═'*width}")
    print(f"  {text}")
    print(f"{'═'*width}{RESET}")


def step(n, title, color=C):
    print(f"\n{color}{BOLD}[Step {n}]{RESET} {BOLD}{title}{RESET}")


def run_demo(
    n_bits: int = 64,
    noise_rate: float = 0.0,
    eve_rate: float = 0.0,
    message: str = "QKD Demo!",
    delay: float = 0.0,
):
    banner(f"BB84 QKD — n={n_bits} bits | noise={noise_rate:.0%} | Eve={eve_rate:.0%}")

    # 1. Alice
    step(1, "Alice generates random bits and bases")
    alice_bits  = generate_bits(n_bits)
    alice_bases = generate_bases(n_bits)
    fb = format_bases(alice_bases)
    print(f"  Alice bits  : {[int(x) for x in alice_bits[:SHOW_BITS]]} …")
    print(f"  Alice bases : {fb[:SHOW_BITS]} …  (+=rectilinear  ×=diagonal)")
    time.sleep(delay)

    # 2. Eve
    step(2, f"Eve intercept-resend attack (rate={eve_rate:.0%})")
    tx_bits, eve_bases = intercept_resend_attack(alice_bits, alice_bases, eve_rate)
    if eve_rate > 0:
        fe = format_bases(eve_bases)
        intercepted = sum(1 for e in eve_bases if e != -1)
        print(f"  {R}Eve intercepted {intercepted}/{n_bits} qubits{RESET}")
        print(f"  Eve bases : {fe[:SHOW_BITS]} …")
    else:
        print(f"  {G}No interception — channel is clean{RESET}")
    time.sleep(delay)

    # 3. Noise
    step(3, f"Channel noise ({noise_rate:.0%} bit-flip probability)")
    noisy_bits = apply_channel_noise(tx_bits, noise_rate)
    flips = int(np.sum(tx_bits != noisy_bits))
    print(f"  Bits flipped by noise: {flips}")
    time.sleep(delay)

    # 4. Bob measures
    step(4, "Bob chooses random bases and measures")
    bob_bases   = generate_bases(n_bits)
    bob_results = measure_bits(noisy_bits, alice_bases, bob_bases)
    fb2 = format_bases(bob_bases)
    print(f"  Bob bases  : {fb2[:SHOW_BITS]} …")
    time.sleep(delay)

    # 5. Sifting
    step(5, "Key sifting — discard mismatched bases")
    a_sift, b_sift, mask = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    kept = int(np.sum(mask))
    print(f"  Kept {kept}/{n_bits} bits ({kept/n_bits:.0%})")
    print(f"  Alice sifted: {[int(x) for x in a_sift[:SHOW_BITS]]} …")
    print(f"  Bob   sifted: {[int(x) for x in b_sift[:SHOW_BITS]]} …")
    time.sleep(delay)

    # 6. QBER
    step(6, "QBER estimation")
    qber, mismatches = calculate_error_rate(a_sift, b_sift)
    colour = G if qber <= QBER_THRESHOLD else R
    print(f"  Mismatches : {mismatches} / {kept}")
    print(f"  QBER       : {colour}{BOLD}{qber:.4f}{RESET}  (threshold = {QBER_THRESHOLD})")
    secure = qber <= QBER_THRESHOLD
    verdict = f"{G}✓ SECURE — proceeding with key{RESET}" if secure else f"{R}✗ EAVESDROPPING DETECTED — session aborted{RESET}"
    print(f"  Verdict    : {verdict}")
    time.sleep(delay)

    if not secure:
        print(f"\n{R}Demo ends here: channel not trusted.{RESET}\n")
        return

    # 7. Reconciliation
    step(7, "Information reconciliation (CASCADE, 5 passes)")
    a_rec, b_rec, corrections = reconcile_keys(a_sift, b_sift)
    q_after, _ = calculate_error_rate(a_rec, b_rec)
    print(f"  Corrections made : {corrections}")
    print(f"  QBER after       : {G}{q_after:.6f}{RESET}")
    time.sleep(delay)

    # 8. Privacy amplification
    step(8, "Privacy amplification → 128-bit AES key (SHA-256)")
    eve_info = estimate_eve_information(qber, kept)
    print(f"  Estimated Eve's knowledge: {eve_info:.1f} bits")
    alice_key = privacy_amplification(a_rec)
    bob_key   = privacy_amplification(b_rec)
    match = alice_key == bob_key
    print(f"  Alice key : {C}{alice_key.hex()}{RESET}")
    print(f"  Bob   key : {C}{bob_key.hex()}{RESET}")
    print(f"  Keys match: {G+'✓ YES'+RESET if match else R+'✗ NO'+RESET}")
    time.sleep(delay)

    # 9. Hybrid encryption
    step(9, f"Hybrid AES-CTR encryption")
    print(f"  Plaintext : {Y}'{message}'{RESET}")
    hybrid = run_hybrid_demo(alice_key, bob_key, message)
    print(f"  Ciphertext: {M}{hybrid['ciphertext_hex']}{RESET}")
    ok = hybrid["decryption_success"]
    print(f"  Decrypted : {G if ok else R}'{hybrid.get('decrypted_message', 'ERROR')}'{RESET}")
    print(f"  Success   : {G+'✓'+RESET if ok else R+'✗'+RESET}")
    time.sleep(delay)

    banner("Demo complete!", color=G)


def interactive_menu():
    print(f"\n{BOLD}{B}═══════════════════════════════════════{RESET}")
    print(f"{BOLD}  BB84 QKD Interactive Demo  {RESET}")
    print(f"{BOLD}{B}═══════════════════════════════════════{RESET}\n")
    print("Scenarios:")
    print(f"  {G}1{RESET}. Ideal channel (no noise, no Eve)")
    print(f"  {Y}2{RESET}. Noisy channel only (5% noise)")
    print(f"  {R}3{RESET}. Full Eve attack (100% interception)")
    print(f"  {M}4{RESET}. Partial Eve (25%) + noise (2%)")
    print(f"  {C}5{RESET}. Custom parameters")
    print(f"  {W}0{RESET}. Run all scenarios\n")

    choice = input("Select scenario [0-5]: ").strip()

    if choice == "1":
        run_demo(n_bits=64, noise_rate=0.0, eve_rate=0.0,
                 message="Secure QKD works!", delay=0.3)
    elif choice == "2":
        run_demo(n_bits=64, noise_rate=0.05, eve_rate=0.0,
                 message="Noisy but secure!", delay=0.3)
    elif choice == "3":
        run_demo(n_bits=64, noise_rate=0.0, eve_rate=1.0,
                 message="Eve is watching!", delay=0.3)
    elif choice == "4":
        run_demo(n_bits=64, noise_rate=0.02, eve_rate=0.25,
                 message="Partial attack!", delay=0.3)
    elif choice == "5":
        n     = int(input("  Number of bits [default 64]: ") or 64)
        noise = float(input("  Noise rate 0.0–0.1 [default 0.0]: ") or 0.0)
        eve   = float(input("  Eve interception rate 0.0–1.0 [default 0.0]: ") or 0.0)
        msg   = input("  Message [default 'Hello QKD!']: ") or "Hello QKD!"
        run_demo(n_bits=n, noise_rate=noise, eve_rate=eve, message=msg, delay=0.2)
    elif choice == "0":
        for label, kwargs in [
            ("Ideal", dict(n_bits=64, noise_rate=0.0, eve_rate=0.0, message="Ideal QKD!")),
            ("Noisy", dict(n_bits=64, noise_rate=0.05, eve_rate=0.0, message="Noisy!")),
            ("Full Eve", dict(n_bits=64, noise_rate=0.0, eve_rate=1.0, message="Eve!")),
            ("Partial Eve + Noise", dict(n_bits=64, noise_rate=0.02, eve_rate=0.25, message="Mixed!")),
        ]:
            print(f"\n{'='*60}\n  SCENARIO: {label}\n{'='*60}")
            run_demo(**kwargs, delay=0.0)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    interactive_menu()
