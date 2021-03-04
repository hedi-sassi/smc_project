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
        val = add_mod(self.value, other.value)
        return Share(val)

    def __sub__(self, other):
        val = sub_mod(self.value, other.value)
        return Share(val)

    def __mul__(self, other):
        val = mul_mod(self.value, other.value)
        return Share(val)


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    
    shares = []
    last_share_value = secret
    for _ in range(num_shares -1):

        share_value = random.randint(0, get_mod())

        shares.append(Share(share_value))
        last_share_value = sub_mod(last_share_value, share_value)

    shares.append(Share(last_share_value))

    return shares

    

def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    
    res = 0

    for share in shares :
        res = add_mod(share.value, res)

    return res


def add_mod(a, b) -> int:
    """Add modulo 2^64"""

    return (a + b) % get_mod()

def sub_mod(a, b) -> int:
    """Sub modulo 2^64"""

    return (a - b) % get_mod()

def mul_mod(a, b) -> int:
    """Mul modulo 2^64"""

    return (a * b) % get_mod()

# size of the additive integer field
max_nbr = 2**64

def get_mod() -> int:
    """Return the moddulus for the integer Field 2^64"""

    return max_nbr