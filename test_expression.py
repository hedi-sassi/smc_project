"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar


# Example test, you can adapt it to your needs.
def test_expr_construction():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b) * c * Scalar(4) + Scalar(3)
    assert repr(expr) == "((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3))"


def test1():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b) * c - (Scalar(4) + Scalar(3))
    assert repr(expr) == "((Secret(1) + Secret(2)) * Secret(3) - (Scalar(4) + Scalar(3)))"


def test2():
    a = Secret(14)
    b = Secret(3)
    expr = (a - b)
    assert repr(expr) == "(Secret(14) - Secret(3))"


def test3():
    a = Secret(3)
    b = Secret(14)
    c = Secret(2)
    expr = ((a + b + c) * Scalar(5))
    assert repr(expr) == "((Secret(3) + Secret(14) + Secret(2)) * Scalar(5))"


def test4():
    a = Secret(3)
    b = Secret(14)
    c = Secret(2)
    expr = ((a * b + b * Scalar(4)) * c - (a + Scalar(1) * b))
    assert repr(expr) == "((Secret(3) * Secret(14) + Secret(14) * Scalar(4)) * Secret(2) - (Secret(3) + Scalar(1) * Secret(14)))"
