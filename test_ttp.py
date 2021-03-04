"""
Unit tests for the trusted parameter generator.
Testing ttp is not obligatory.

MODIFY THIS FILE.
"""

from ttp import *
from secret_sharing import *

from ttp import TrustedParamGenerator


def test():
    
    ttp = TrustedParamGenerator()

    ttp.add_participant("Alice")
    ttp.add_participant("Bob")
    ttp.add_participant("Charlie")

    operation_id = "1"

    alice_shares = ttp.retrieve_share("Alice", operation_id)
    bob_shares = ttp.retrieve_share("Bob", operation_id)
    charlie_shares = ttp.retrieve_share("Charlie", operation_id)

    a = reconstruct_secret(list({alice_shares[0], bob_shares[0], charlie_shares[0]}))
    b = reconstruct_secret(list({alice_shares[1], bob_shares[1], charlie_shares[1]}))
    c = reconstruct_secret(list({alice_shares[2], bob_shares[2], charlie_shares[2]}))

    assert a * b == c