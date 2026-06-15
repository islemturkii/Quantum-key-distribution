import numpy as np


def generate_bases(n: int) -> np.ndarray:
    """
    Generate random BB84 bases.

    0 -> rectilinear basis (+)
    1 -> diagonal basis (x)
    """
    if n <= 0:
        raise ValueError("Number of bases must be positive.")

    return np.random.randint(0, 2, size=n)


def format_bases(bases: np.ndarray) -> list[str]:
    """
    Convert numeric basis representation into readable symbols.

    0  -> +
    1  -> x
    -1 -> no interception / not applicable
    """
    formatted = []

    for basis in bases:
        if basis == 0:
            formatted.append("+")
        elif basis == 1:
            formatted.append("x")
        else:
            formatted.append("-")

    return formatted