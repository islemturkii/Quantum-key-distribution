import numpy as np


def measure_bits(transmitted_bits, transmitted_bases, bob_bases):
    """
    Simulate Bob's measurement process.

    If Bob uses the same basis as the transmitted basis, he obtains
    the correct bit. If the bases differ, the result is random.
    """
    bob_results = []

    for bit, transmitted_basis, bob_basis in zip(
        transmitted_bits, transmitted_bases, bob_bases
    ):
        if transmitted_basis == bob_basis:
            bob_results.append(bit)
        else:
            bob_results.append(np.random.randint(0, 2))

    return np.array(bob_results)


