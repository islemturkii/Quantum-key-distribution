import numpy as np


def apply_channel_noise(bits, noise_rate=0.0):
    """
    Simulate channel noise by randomly flipping bits.

    noise_rate = probability that each bit is flipped.
    Example:
        noise_rate = 0.05 means 5% of bits may be corrupted.
    """
    if noise_rate < 0 or noise_rate > 1:
        raise ValueError("Noise rate must be between 0 and 1.")

    noisy_bits = bits.copy()

    for i in range(len(noisy_bits)):
        if np.random.random() < noise_rate:
            noisy_bits[i] = 1 - noisy_bits[i]

    return noisy_bits