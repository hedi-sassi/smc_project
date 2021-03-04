"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

import collections
import random
import sys
from secret_sharing import *
from typing import (
    Dict,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import(
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.triplets_shares: Dict[str, Dict[str, Tuple[Share, Share, Share]]] = dict()


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id. And operation id.
        """

        if client_id not in self.participant_ids:
            return None

        # first check if dict not already generated
        if op_id in self.triplets_shares:
            return self.triplets_shares[op_id][client_id]

        else:
            # generate the dict corresponding to this new operation and return result
            self.gen_beaver(op_id)
            print(self.triplets_shares)
            return self.triplets_shares[op_id][client_id]

 
    def gen_beaver(self, op_id):
        """Generates a new dictionnary containing all beaver triplets for each client for a specific operation indexed by op_id"""

        a = random.randint(0, get_mod())
        b = random.randint(0, get_mod())

        c = mul_mod(a, b)
        print(str(a)+" <-a "+str(b)+" <-b "+str(c)+" <-c ")
        print(len(self.participant_ids))

        # generate shares of beaver triplets
        a_shares = share_secret(a, len(self.participant_ids))
        b_shares = share_secret(b, len(self.participant_ids))
        c_shares = share_secret(c, len(self.participant_ids))

        print(a_shares)

        # store shares in a dict
        res = dict()

        for i, name in enumerate(self.participant_ids) :
            l = list()
            l.append(a_shares[i])
            l.append(b_shares[i])
            l.append(c_shares[i])
            
            res[name] = tuple(l)

        # index dict w.r.t the operation id
        self.triplets_shares[op_id] = res
