"""
main.py — CR-5 QKD Project Entry Point
=======================================
Run any part of the project from here.

Usage:
  python3 main.py demo          # interactive BB84 demo
  python3 main.py evaluate      # run full evaluation & generate figures
  python3 main.py test          # run unit test suite
  python3 main.py quick         # run all 4 scenarios non-interactively
"""
import sys, os

def usage():
    print(__doc__)
    sys.exit(0)

def cmd_demo():
    from demo.interactive_demo import interactive_menu
    interactive_menu()

def cmd_evaluate():
    from evaluate import run_evaluation, plot_qber_vs_interception, \
        plot_acceptance_vs_interception, plot_qber_heatmap, \
        plot_bb84_error_comparison, plot_bb84_full_comparison, \
        plot_reconciliation_effectiveness
    rows = run_evaluation()
    print("\nGenerating all figures...")
    plot_qber_vs_interception(rows)
    plot_acceptance_vs_interception(rows)
    plot_qber_heatmap(rows)
    plot_bb84_error_comparison()
    plot_bb84_full_comparison()
    plot_reconciliation_effectiveness(rows)
    print("\nDone! Figures saved in results/figures/")

def cmd_test():
    os.system(f"{sys.executable} tests/test_bb84.py")

def cmd_quick():
    from src.bb84_protocol import run_bb84
    scenarios = [
        ("Ideal (no noise, no Eve)",        dict(noise_rate=0.0, eve_interception_rate=0.0)),
        ("Noisy channel only (5%)",          dict(noise_rate=0.05, eve_interception_rate=0.0)),
        ("Full Eve (100% interception)",     dict(noise_rate=0.0, eve_interception_rate=1.0)),
        ("Partial Eve (25%) + noise (2%)",  dict(noise_rate=0.02, eve_interception_rate=0.25)),
    ]
    for title, kwargs in scenarios:
        print(f"\n{'='*55}\n  {title}\n{'='*55}")
        r = run_bb84(n_bits=256, message="Quantum Key Distribution works!", **kwargs)
        print(f"\n  Summary: QBER={r['qber']:.4f}  Secure={r['secure']}  "
              f"KeysMatch={r['keys_match']}  DecryptOK={r['decryption_success']}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    dispatch = {"demo": cmd_demo, "evaluate": cmd_evaluate,
                "test": cmd_test, "quick": cmd_quick}
    if cmd in dispatch:
        dispatch[cmd]()
    else:
        usage()
