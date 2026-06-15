import numpy as np


def intercept_resend_attack(alice_bits, alice_bases, interception_rate=1.0):
    """
    Simulate Eve's intercept-resend attack.

    interception_rate controls how many transmitted bits Eve attacks.
    Example:
        1.0 = Eve attacks all bits
        0.3 = Eve attacks 30% of bits
        0.0 = Eve does not attack
    """
    if interception_rate < 0 or interception_rate > 1:
        raise ValueError("Interception rate must be between 0 and 1.")

    n = len(alice_bits)
    eve_bases = np.full(n, -1)
    transmitted_bits = alice_bits.copy()

    for i in range(n):
        if np.random.random() < interception_rate:
            eve_basis = np.random.randint(0, 2)
            eve_bases[i] = eve_basis

            if alice_bases[i] == eve_basis:
                transmitted_bits[i] = alice_bits[i]
            else:
                transmitted_bits[i] = np.random.randint(0, 2)

    return transmitted_bits, eve_bases