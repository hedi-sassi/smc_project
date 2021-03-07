"""
Integration tests that verify different aspects of the protocol.
You can *add* new tests here, but it is best to  add them to a new test file.

ALL EXISTING TESTS IN THIS SUITE SHOULD PASS WITHOUT ANY MODIFICATION TO THEM.
"""

import time
from multiprocessing import Process, Queue

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results


def suite(parties, expr, expected):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    results = run_processes(participants, *clients)

    for result in results:
        assert result == expected


def test_suite1():
    """
    f(a, b, c) = a + b + c
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (alice_secret + bob_secret + charlie_secret)
    expected = 3 + 14 + 2
    suite(parties, expr, expected)


def test_suite2():
    """
    f(a, b) = a - b
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
    }

    expr = (alice_secret - bob_secret)
    expected = 14 - 3
    suite(parties, expr, expected)


def test_suite3():
    """
    f(a, b, c) = (a + b + c) ∗ K
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = ((alice_secret + bob_secret + charlie_secret) * Scalar(5))
    expected = (3 + 14 + 2) * 5
    suite(parties, expr, expected)


def test_suite4():
    """
    f(a, b, c) = (a + b + c) + K
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = ((alice_secret + bob_secret + charlie_secret) + Scalar(5))
    expected = (3 + 14 + 2) + 5
    suite(parties, expr, expected)


def test_suite5():
    """
    f(a, b, c) = (a ∗ K0 + b - c) + K1
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (((alice_secret * Scalar(5)) + bob_secret - charlie_secret) + Scalar(9))
    expected = ((3 * 5) + 14 - 2) + 9
    suite(parties, expr, expected)


def test_suite6():
    """
    f(a, b, c, d) = a + b + c + d
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    david_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2},
        "David": {david_secret: 5}
    }

    expr = (alice_secret + bob_secret + charlie_secret + david_secret)
    expected = 3 + 14 + 2 + 5
    suite(parties, expr, expected)


def test_suite7():
    """
    f(a, b, c) = (a ∗ b) + (b ∗ c) + (c ∗ a)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (
            (alice_secret * bob_secret) +
            (bob_secret * charlie_secret) +
            (charlie_secret * alice_secret)
    )
    expected = ((3 * 14) + (14 * 2) + (2 * 3))
    suite(parties, expr, expected)


def test_suite8():
    """
    f(a, b, c, d, e) = ((a + K0) + b ∗ K1 - c) ∗ (d + e)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    david_secret = Secret()
    elusinia_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2},
        "David": {david_secret: 5},
        "Elusinia": {elusinia_secret: 7}
    }

    expr = (
            (
                    (alice_secret + Scalar(8)) +
                    ((bob_secret * Scalar(9)) - charlie_secret)
            ) * (david_secret + elusinia_secret)
    )
    expected = (((3 + 8) + (14 * 9) - 2) * (5 + 7))
    suite(parties, expr, expected)


def test_suite_constantes():
    """
    f(a, b) = K1 + K2
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
    }

    expr = (Scalar(2) + Scalar(1))
    expected = 3
    suite(parties, expr, expected)


def test_suite_two_parties():
    """
    f(a, b) = a + b 
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
    }

    expr = (alice_secret + bob_secret)
    expected = 3 + 14
    suite(parties, expr, expected)


def test_suite_three_parties():
    """
    f(a, b) = a * b * c
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 2},
        "Charlie": {charlie_secret: 1}
    }

    expr = (alice_secret * bob_secret * charlie_secret)
    expected = (3 * 2 * 1)
    suite(parties, expr, expected)


def test_suite_const_mul_secret():
    """
        f(a, b) = a * K
    """
    alice_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
    }

    expr = (alice_secret * Scalar(2))
    expected = (3 * 2)
    suite(parties, expr, expected)


def test_suite_const_mul_secret2():
    """
        f(a, b) = K * K * a
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 4},
    }

    expr = (Scalar(3) * Scalar(3) * alice_secret)
    expected = (3 * 3 * 3)
    suite(parties, expr, expected)

def test_suite_three_parties_double_secret():
    """
    f(a, b) = a1 + b1 + b2 + a2 + c
    """
    alice_secret1 = Secret()
    alice_secret2 = Secret()
    bob_secret1 = Secret()
    bob_secret2 = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret1: 3,alice_secret2: 4},
        "Bob": {bob_secret1: 2, bob_secret2: 12},
        "Charlie": {charlie_secret: 1}
    }

    expr = (alice_secret1 + bob_secret1 + bob_secret2 + alice_secret2 + charlie_secret)
    expected = (3 + 4 + 12 + 2 + 1)
    suite(parties, expr, expected)

def test_suite_three_parties_double_secret_mult():
    """
    f(a, b) = a1 * a2 + b1 * b2 + c
    """
    alice_secret1 = Secret()
    alice_secret2 = Secret()
    bob_secret1 = Secret()
    bob_secret2 = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret1: 3,alice_secret2: 4},
        "Bob": {bob_secret1: 2, bob_secret2: 12},
        "Charlie": {charlie_secret: 1}
    }

    expr = (alice_secret1 * alice_secret2 + bob_secret1 * bob_secret2 + charlie_secret)
    expected = (3 * 4 + 2 * 12 + 1)
    suite(parties, expr, expected)

def test_suite_three_parties_double_secret_double_use():
    """
    f(a, b) = a1 * a2 + b1 * b2 + c * a2 * b1
    """
    alice_secret1 = Secret()
    alice_secret2 = Secret()
    bob_secret1 = Secret()
    bob_secret2 = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret1: 3,alice_secret2: 4},
        "Bob": {bob_secret1: 2, bob_secret2: 12},
        "Charlie": {charlie_secret: 1}
    }

    expr = (alice_secret1 * alice_secret2 + bob_secret1 * bob_secret2 + charlie_secret * alice_secret2 * bob_secret2)
    expected = (3 * 4 + 2 * 12 + 1 * 4 * 12)
    suite(parties, expr, expected)