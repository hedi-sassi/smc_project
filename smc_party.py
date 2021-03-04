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
                    self.comm.publish_message(pid + "_" + str(s.get_id_int()), str(shares[i].value))
                    #print("####################################### Publish "+pid + "_" + str(s.get_id_int())+" with value "+str(shares[i].value))
                else:
                    # Keep own share in dict
                    self.own_shares[str(s.get_id_int())] = shares[i]

        #compute locally share of the final value
        final_share = self.process_expression(self.protocol_spec.expr).value

        #send final share to others
        self.comm.publish_message("final", str(final_share))

        # put every share of the circuit together
        final_result = Share(final_share)

        for pid in self.protocol_spec.participant_ids:

            if pid != self.client_id:
                remote_share = self.comm.retrieve_public_message(pid, "final")

                while remote_share is None: #retry if not yet here

                    remote_share = self.comm.retrieve_public_message(pid, "final")
                #print("#######################################"+str(int(remote_share)))
                final_result += Share(int(remote_share))

        #print("#######################################"+str(final_result))
        return final_result.value


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression,
            mult = False
    ) -> Share:

        if isinstance(expr, Addition):  # if expr is an addition operation:
            return self.process_expression(expr.e1) + self.process_expression(expr.e2)

        if isinstance(expr, Substraction):  # if expr is an addition operation:
            return self.process_expression(expr.e1) - self.process_expression(expr.e2)

        if isinstance(expr, Multiplication):

            if isinstance(expr.e1, Secret) and isinstance(expr.e2, Secret):
                x = self.process_expression(expr.e1, True)
                y = self.process_expression(expr.e2, True)

                x_minus_a, y_minus_b, c = self.get_beaver_shares(x, y, expr)

                if self.client_id == self.protocol_spec.participant_ids[0]:     #participant 0 add the constant
                    return  c + x * y_minus_b + y * x_minus_a - x_minus_a * y_minus_b
                else:
                    return  c + x * y_minus_b + y * x_minus_a

            elif isinstance(expr.e1, Scalar) and isinstance(expr.e1, Scalar):

                if self.client_id == self.protocol_spec.participant_ids[0]: # only the first participant operates on scalars
                    return self.process_expression(expr.e1, True) * self.process_expression(expr.e2, True)

                else:   #others participants need to perform neutral operation * 1 or + 0 depending if mult or add
                    return Share(1) if mult else Share(0)
                
            else:
                return self.process_expression(expr.e1, True) * self.process_expression(expr.e2, True)

        if isinstance(expr, Secret):
            if str(expr.get_id_int()) in self.own_shares.keys():
                return self.own_shares[str(expr.get_id_int())]
            else:
                return Share(self.search_share(expr.get_id_int()))

        if isinstance(expr, Scalar):    # scalar should only be added by one participant in case of addition
            if not mult and self.protocol_spec.participant_ids[0] != self.client_id:
                return Share(0)
            else:
                return Share(expr.value)
        #
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.


    def search_share(self, expr_id) -> int:
        """Search for corresponding secret on the server"""

        for name in self.protocol_spec.participant_ids:
            if name != self.client_id:
                res = self.comm.retrieve_public_message(name, self.client_id + "_" + str(expr_id))
                #print("####################################### Search result for"+name+" request from "+self.client_id+str(int(res)))
                if res is not None:
                    return int(res)
        return None


    def get_beaver_shares(self, x, y, expr) :
        print(str(expr.get_id_int()))
        a, b, c = self.comm.retrieve_beaver_triplet_shares(str(expr.get_id_int()))

        #send to others shares of x-a and y-b
        x_minus_a_share = x - Share(a)
        y_minus_b_share = y - Share(b)

        self.comm.publish_message(self.client_id+"x_minus_a", str(x_minus_a_share.value))
        self.comm.publish_message(self.client_id+"y_minus_b", str(y_minus_b_share.value))

        #reconstruct x -a and y-b 

        x_shares = x_minus_a_share
        y_shares = y_minus_b_share

        for pid in self.protocol_spec.participant_ids:

            if pid != self.client_id:

                curr_x = self.comm.retrieve_public_message(pid, pid+"x_minus_a")
                curr_y = self.comm.retrieve_public_message(pid, pid+"y_minus_b")

                while curr_x is None:               #wait for others to upload their shares
                    curr_x = self.comm.retrieve_public_message(pid, pid+"x_minus_a")

                while curr_y is None:
                    curr_y = self.comm.retrieve_public_message(pid, pid+"y_minus_b")

                x_shares += Share(int(curr_x))
                y_shares += Share(int(curr_y))

        return x_shares, y_shares, Share(c)
