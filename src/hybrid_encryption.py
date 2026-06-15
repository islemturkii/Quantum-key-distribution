"""
hybrid_encryption.py — AES-CTR hybrid encryption using QKD-derived key
Uses the `cryptography` stdlib-compatible package (not pycryptodome).
"""
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def encrypt_message(key: bytes, plaintext: str):
    """Encrypt plaintext with AES-CTR using a 128-bit key."""
    nonce = os.urandom(16)                             # 128-bit nonce for CTR
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    enc = cipher.encryptor()
    ciphertext = enc.update(plaintext.encode("utf-8")) + enc.finalize()
    return nonce, ciphertext


def decrypt_message(key: bytes, nonce: bytes, ciphertext: bytes) -> str:
    """Decrypt AES-CTR ciphertext."""
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    dec = cipher.decryptor()
    return (dec.update(ciphertext) + dec.finalize()).decode("utf-8")


def run_hybrid_demo(alice_key: bytes, bob_key: bytes, message: str) -> dict:
    result = {
        "message": message,
        "alice_key_hex": alice_key.hex(),
        "bob_key_hex":   bob_key.hex(),
        "keys_match":    alice_key == bob_key,
        "encryption_success": False,
        "decryption_success": False,
        "decrypted_message":  None,
        "ciphertext_hex":     None,
    }
    try:
        nonce, ciphertext = encrypt_message(alice_key, message)
        result["ciphertext_hex"]     = ciphertext.hex()
        result["encryption_success"] = True
        decrypted = decrypt_message(bob_key, nonce, ciphertext)
        result["decrypted_message"]  = decrypted
        result["decryption_success"] = (decrypted == message)
    except Exception as e:
        result["decryption_error"] = str(e)
    return result
