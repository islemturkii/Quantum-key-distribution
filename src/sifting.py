def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """
    Perform BB84 key sifting.

    Alice and Bob keep only positions where they used the same basis.
    """
    matching_positions = alice_bases == bob_bases

    sifted_alice = alice_bits[matching_positions]
    sifted_bob = bob_results[matching_positions]

    return sifted_alice, sifted_bob, matching_positions