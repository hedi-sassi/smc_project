import random
import time
from multiprocessing import Process, Queue

from expression import Scalar, Secret
from protocol import ProtocolSpec
from secret_sharing import get_mod
from server import run

from smc_party import SMCParty
import os

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
    # print(f"{client_id} has finished!")


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

    for _ in clients:
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


participants_n = [2, 5, 10, 20, 50, 100]
ops_n = [10, 100, 500, 1000]
repeat_experiment = 20


def fixed_circuit_more_participants():
    """
    f(a, b, c, ...) = (K + a) * b
    """
    for _ in range(repeat_experiment):
        for num_part in participants_n:

            circuit = Scalar(56)
            parties = {}

            for p in range(num_part):

                party_secret = Secret()
                parties[str(p)] = {party_secret: p + 69420}

                if p == 0:
                    circuit += party_secret
                if p == 1:
                    circuit *= party_secret

            expected = (56 + 69420) * 69421
            suite(parties, circuit, expected)


def add_scalar():
    for _ in range(repeat_experiment):
        for num_ops in ops_n:

            circuit = Scalar(0)
            parties = {}
            total = 0

            # Generate parties
            for p in range(10):
                party_secret = Secret()
                val = random.randint(0, get_mod())
                parties[str(p)] = {party_secret: val}

            for o in range(num_ops):

                val = random.randint(0, get_mod())

                if o == 0:
                    circuit = Scalar(val)
                else:
                    circuit += Scalar(val)

                total = (total + val) % get_mod()

            suite(parties, circuit, total)


def add_secret():
    for _ in range(repeat_experiment):
        for num_ops in ops_n:

            circuit = Scalar(0)
            parties = {}
            total = 0

            # Generate parties
            for p in range(10):
                party_secret = Secret()
                val = random.randint(0, get_mod())
                parties[str(p)] = {party_secret: val}

            for o in range(num_ops):

                if o == 0:
                    circuit = list(parties[str(o % 10)].keys())[0]
                else:
                    circuit += list(parties[str(o % 10)].keys())[0]

                total = (total + list(parties[str(o % 10)].values())[0]) % get_mod()

            suite(parties, circuit, total)


def mul_scalar():
    for _ in range(repeat_experiment):
        for num_ops in ops_n:

            circuit = Scalar(1)
            parties = {}
            total = 1

            # Generate parties
            for p in range(10):
                party_secret = Secret()
                val = random.randint(0, get_mod())
                parties[str(p)] = {party_secret: val}

            for o in range(num_ops):

                val = random.randint(0, get_mod())

                if o == 0:
                    circuit = Scalar(val)
                else:
                    circuit *= Scalar(val)

                total = (total * val) % get_mod()

            suite(parties, circuit, total)


def mul_secret():
    for _ in range(repeat_experiment):
        for num_ops in ops_n:

            circuit = Scalar(0)
            parties = {}
            total = 1

            # Generate parties and basic circuit
            for p in range(10):
                party_secret = Secret()
                val = random.randint(0, get_mod())
                parties[str(p)] = {party_secret: val}

            for o in range(num_ops):

                if o == 0:
                    circuit = list(parties[str(o % 10)].keys())[0]
                else:
                    circuit *= list(parties[str(o % 10)].keys())[0]

                total = (total * list(parties[str(o % 10)].values())[0]) % get_mod()

            suite(parties, circuit, total)


if not os.path.exists("metrics"):
    os.mkdir("metrics")

if not os.path.exists("metrics/fixed_circuit_more_participants"):
    os.mkdir("metrics/fixed_circuit_more_participants")

if not os.path.exists("metrics/add_scalar"):
    os.mkdir("metrics/add_scalar")

if not os.path.exists("metrics/add_secret"):
    os.mkdir("metrics/add_secret")

if not os.path.exists("metrics/mul_scalar"):
    os.mkdir("metrics/mul_scalar")

if not os.path.exists("metrics/mul_secret"):
    os.mkdir("metrics/mul_secret")

# fixed_circuit_more_participants()
add_scalar()
# add_secret()
# mul_scalar()
# mul_secret()
