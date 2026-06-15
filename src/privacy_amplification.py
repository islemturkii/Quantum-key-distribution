import numpy as np
import hashlib


def privacy_amplification(key: np.ndarray) -> bytes:
    if len(key) == 0:
        raise ValueError("Cannot amplify an empty key.")
    padded = np.zeros(((len(key) + 7) // 8) * 8, dtype=np.uint8)
    padded[:len(key)] = key
    byte_array = np.packbits(padded).tobytes()
    digest = hashlib.sha256(byte_array).digest()
    return digest[:16]


def estimate_eve_information(qber: float, sifted_length: int) -> float:
    estimated_interception_rate = min(4 * qber, 1.0)
    eve_bits = estimated_interception_rate * sifted_length * 0.5
    return eve_bits