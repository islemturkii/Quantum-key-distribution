import numpy as np


def generate_bits(n: int) -> np.ndarray:
    """
    Generate Alice's random binary bit sequence.

    0 and 1 represent the classical bits that Alice wants to encode
    using BB84 quantum bases.
    """
    if n <= 0:
        raise ValueError("Number of bits must be positive.")

    return np.random.randint(0, 2, size=n)