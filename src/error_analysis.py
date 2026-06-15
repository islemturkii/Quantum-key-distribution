import numpy as np


def calculate_error_rate(alice_key, bob_key):
    """
    Compute the Quantum Bit Error Rate (QBER).

    QBER = number of mismatched bits / total number of sifted bits
    """
    if len(alice_key) == 0:
        return 0.0, 0

    mismatches = int(np.sum(alice_key != bob_key))
    error_rate = mismatches / len(alice_key)

    return error_rate, mismatches