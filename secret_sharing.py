"""
Secret sharing scheme.
"""
import random
import sys 
from typing import List


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, *args, **kwargs):
        # Adapt constructor arguments as you wish
        raise NotImplementedError("You need to implement this method.")

    def __repr__(self):
        # Helps with debugging.
        raise NotImplementedError("You need to implement this method.")

    def __add__(self, other):
        raise NotImplementedError("You need to implement this method.")

    def __sub__(self, other):
        raise NotImplementedError("You need to implement this method.")

    def __mul__(self, other):
        raise NotImplementedError("You need to implement this method.")


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    
    shares = []
    last_share = secret
    for _ in range(num_shares -1):

        share = random.randint(-sys.maxsize, sys.maxsize)

        shares.append(share)
        last_share -= share

    shares.append(last_share)

    return shares

    

def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    raise NotImplementedError("You need to implement this method.")


# Feel free to add as many methods as you want.
