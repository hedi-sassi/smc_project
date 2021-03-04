"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import Addition, Expression, Multiplication, Scalar, Secret, Substraction
from protocol import ProtocolSpec
from secret_sharing import (
    reconstruct_secret,
    share_secret,
    Share,
)


# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
    ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict

        self.secrets = list(value_dict.keys())

        self.own_shares = dict()

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        # Share secrets across participants

        for s in self.secrets:
            shares = share_secret(self.value_dict[s], len(self.protocol_spec.participant_ids))

            for i, pid in enumerate(self.protocol_spec.participant_ids):

                if pid != self.client_id:
                    # Publish shares for other participants
                    self.comm.publish_message(pid + "_" + str(s.get_id_int()), str(shares[i].get_value()))
                else:
                    # Keep own share in dict
                    self.own_shares[str(s.get_id_int())] = shares[i]

        return self.process_expression(self.protocol_spec.expr).value

    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
    ) -> Share:

        if isinstance(expr, Addition):  # if expr is an addition operation:
            return self.process_expression(expr.e1) + self.process_expression(expr.e2)

        if isinstance(expr, Substraction):  # if expr is an addition operation:
            return self.process_expression(expr.e1) - self.process_expression(expr.e2)

        # if expr is a multiplication operation:
        #     ...

        if isinstance(expr, Secret):
            if str(expr.get_id_int()) in self.own_shares.keys():
                return self.own_shares[str(expr.get_id_int())]
            else:
                return Share(self.search_share(expr.get_id_int()))

        if isinstance(expr, Scalar):
            return Share(expr.value)
        #
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
        pass

    def search_share(self, expr_id) -> int:
        """Search for corresponding secret on the server"""

        for name in self.protocol_spec.participant_ids:
            if name != self.client_id:
                res = self.comm.retrieve_public_message(name, self.client_id + "_" + str(expr_id))
                if res is not None:
                    return int(res)
        return None
