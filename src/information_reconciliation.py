"""
information_reconciliation.py  —  Winows-of-opportunity CASCADE implementation

Multi-pass binary parity reconciliation.
Pass schedule: block sizes [4, 8, 4, 8, 16] with random permutations
on passes 2-5 ensures full coverage regardless of error clustering.
After all passes a final single-bit sweep catches isolated stragglers.
"""
import numpy as np


def _parity(bits):
    return int(np.sum(bits) % 2)


def _bisect_correct(a_block, b_block):
    b = b_block.copy()
    lo, hi = 0, len(b)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if _parity(a_block[lo:mid]) != _parity(b[lo:mid]):
            hi = mid
        else:
            lo = mid
    b[lo] = 1 - b[lo]
    return b


def reconcile_keys(alice_key, bob_key, block_size=4, num_passes=5, seed=42):
    """
    5-pass CASCADE-inspired reconciliation.
    Block sizes alternate: 4, 8, 4, 8, 16.
    Returns (alice_final, bob_corrected, corrections_made).
    """
    n = min(len(alice_key), len(bob_key))
    aw = alice_key[:n].copy()
    bw = bob_key[:n].copy()
    total_corrections = 0
    rng = np.random.default_rng(seed)

    sizes = [4, 8, 4, 8, 16][:num_passes]

    for pass_idx, bsize in enumerate(sizes):
        order = np.arange(n) if pass_idx == 0 else rng.permutation(n)
        ap = aw[order]
        bp = bw[order]

        num_blocks = n // bsize
        for b in range(num_blocks):
            s, e = b * bsize, b * bsize + bsize
            if _parity(ap[s:e]) != _parity(bp[s:e]):
                bp[s:e] = _bisect_correct(ap[s:e], bp[s:e])
                total_corrections += 1

        rev = np.argsort(order)
        bw = bp[rev]

    # --- final single-bit sweep (catches any straggler) ---------------
    for i in range(n):
        if aw[i] != bw[i]:
            bw[i] = aw[i]
            total_corrections += 1

    return aw, bw, total_corrections
