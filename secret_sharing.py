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

    def __init__(
        self,
        value: int = 0
        ):

        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

    def __add__(self, other):
        val = self.value + other.value
        return Share(val)

    def __sub__(self, other):
        val = self.value - other.value
        return Share(val)

    def __mul__(self, other):
        val = self.value * other.value
        return Share(val)


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    
    shares = []
    last_share_value = secret
    for _ in range(num_shares -1):

        share_value = random.randint(-sys.maxsize, sys.maxsize)

        shares.append(Share(share_value))
        last_share_value -= share_value

    shares.append(Share(last_share_value))

    return shares

    

def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    
    res = 0

    for i in range(len(shares)):
        res += shares[i].value

    return res


