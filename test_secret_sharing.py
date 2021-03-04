"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""

from secret_sharing import share_secret, reconstruct_secret


def test():
    
    test_value = 15
    nbr_participants = 10

    shares = share_secret(test_value, nbr_participants)

    recovered_value = reconstruct_secret(shares)

    assert recovered_value == test_value
