"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional

ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


def operation_formatting(op, depth: int = 0) -> str:

    res = ""

    if not isinstance(op, (Scalar, Secret)):

        if isinstance(op, Multiplication):
            if isinstance(op.e1, (Scalar, Secret, Multiplication)) and isinstance(op.e2, (Scalar, Secret, Multiplication)):
                res = f"{operation_formatting(op.e1, depth+1)}{op.op}{operation_formatting(op.e2, depth+1)}"

            elif isinstance(op.e1, (Scalar, Secret)) and not isinstance(op.e2, (Scalar, Secret, Multiplication)):
                res = f"{operation_formatting(op.e1, depth + 1)}{op.op}({operation_formatting(op.e2, depth + 1)})"

            elif not isinstance(op.e1, (Scalar, Secret, Multiplication)) and isinstance(op.e2, (Scalar, Secret)):
                res = f"({operation_formatting(op.e1, depth + 1)}){op.op}{operation_formatting(op.e2, depth + 1)}"

            else:
                res = f"({operation_formatting(op.e1, depth + 1)}){op.op}({operation_formatting(op.e2, depth + 1)})"

        elif isinstance(op, Substraction):
            if not isinstance(op.e2, (Scalar, Secret)):
                res = f"{operation_formatting(op.e1, depth + 1)}{op.op}({operation_formatting(op.e2, depth + 1)})"

            else:
                res = f"{operation_formatting(op.e1, depth + 1)}{op.op}{operation_formatting(op.e2, depth + 1)}"

        else:
            res = f"{operation_formatting(op.e1, depth + 1)}{op.op}{operation_formatting(op.e2, depth + 1)}"

    else:
        res = f"{repr(op)}"

    return res if depth != 0 else f"({res})"


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
    ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        return Addition(self, other)

    def __sub__(self, other):
        return Substraction(self, other)

    def __mul__(self, other):
        return Multiplication(self, other)

    def __hash__(self):
        return hash(self.id)

    def get_id_int(self):
        return int.from_bytes(base64.b64decode(self.id), byteorder='big', signed=False)


class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __hash__(self):
        return

    # Feel free to add as many methods as you like.


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
            self,
            value: Optional[int] = None,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )

    # Feel free to add as many methods as you like.


class Addition(Expression):
    """Term representing an addition between two Expressions"""

    def __init__(
            self,
            e1: Expression,
            e2: Expression,
            id: Optional[bytes] = None):
        self.e1 = e1
        self.e2 = e2
        self.op = " + "
        super().__init__(id)

    def __repr__(self):
        return (
            f"{operation_formatting(self)}"
        )


class Substraction(Expression):
    """Term representing an substraction between two Expressions"""

    def __init__(
            self,
            e1: Expression,
            e2: Expression,
            id: Optional[bytes] = None):
        self.e1 = e1
        self.e2 = e2
        self.op = " - "
        super().__init__(id)

    def __repr__(self):
        return (
            f"{operation_formatting(self)}"
        )


class Multiplication(Expression):
    """Term representing an substraction between two Expressions"""

    def __init__(
            self,
            e1: Expression,
            e2: Expression,
            id: Optional[bytes] = None):
        self.e1 = e1
        self.e2 = e2
        self.op = " * "
        super().__init__(id)

    def __repr__(self):
        return (
            f"{operation_formatting(self)}"
        )
