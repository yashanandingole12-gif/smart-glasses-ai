import pytest
from backend.app.services.math_engine import math_engine

def test_arithmetic_basic():
    res = math_engine.evaluate("27 × 38")
    assert res is not None
    assert res["result"] == 1026
    assert "1,026" in res["text_response"] or "1026" in res["text_response"]

    res = math_engine.evaluate("125 * 16")
    assert res is not None
    assert res["result"] == 2000

    res = math_engine.evaluate("144 / 12")
    assert res is not None
    assert res["result"] == 12

    res = math_engine.evaluate("25 + 37")
    assert res is not None
    assert res["result"] == 62

    res = math_engine.evaluate("100 - 43")
    assert res is not None
    assert res["result"] == 57

def test_verbal_and_hinglish_arithmetic():
    res = math_engine.evaluate("what is 27 multiplied by 38?")
    assert res is not None
    assert res["result"] == 1026

    res = math_engine.evaluate("bhai 27 into 38 kitna hota hai")
    assert res is not None
    assert res["result"] == 1026

    res = math_engine.evaluate("100 minus 43 kitna hoga?")
    assert res is not None
    assert res["result"] == 57

    res = math_engine.evaluate("125 divided by 5")
    assert res is not None
    assert res["result"] == 25

def test_multiplication_tables():
    res = math_engine.evaluate("table of 7")
    assert res is not None
    assert res["operation"] == "table"
    assert len(res["table"]) == 10
    assert "7 × 1 = 7" in res["table"][0]
    assert "7 × 10 = 70" in res["table"][-1]

    res = math_engine.evaluate("7 ka table")
    assert res is not None
    assert res["operation"] == "table"
    assert res["number"] == 7

    res = math_engine.evaluate("table of 12")
    assert res is not None
    assert "12 × 1 = 12" in res["table"][0]
    assert "12 × 10 = 120" in res["table"][-1]

def test_reciprocals():
    res = math_engine.evaluate("reciprocal of 5")
    assert res is not None
    assert res["result"] == 0.2
    assert "0.2" in res["text_response"]

    res = math_engine.evaluate("reciprocal of 8")
    assert res is not None
    assert res["result"] == 0.125

    res = math_engine.evaluate("1/8")
    assert res is not None
    assert res["result"] == 0.125

def test_percentages():
    res = math_engine.evaluate("15% of 800")
    assert res is not None
    assert res["result"] == 120
    assert "120" in res["text_response"]

    res = math_engine.evaluate("15 percent of 800")
    assert res is not None
    assert res["result"] == 120

    res = math_engine.evaluate("increase 500 by 12%")
    assert res is not None
    assert res["result"] == 560

    res = math_engine.evaluate("decrease 200 by 10%")
    assert res is not None
    assert res["result"] == 180

def test_powers_and_roots():
    res = math_engine.evaluate("2 squared")
    assert res is not None
    assert res["result"] == 4

    res = math_engine.evaluate("5 cubed")
    assert res is not None
    assert res["result"] == 125

    res = math_engine.evaluate("2^10")
    assert res is not None
    assert res["result"] == 1024

    res = math_engine.evaluate("square root of 144")
    assert res is not None
    assert res["result"] == 12

    res = math_engine.evaluate("sqrt 144")
    assert res is not None
    assert res["result"] == 12

    res = math_engine.evaluate("cube root of 27")
    assert res is not None
    assert res["result"] == 3

def test_fraction_arithmetic():
    res = math_engine.evaluate("3/4 + 1/2")
    assert res is not None
    assert res["fraction_result"] == "5/4"
    assert res["result"] == 1.25

def test_non_math_returns_none():
    assert math_engine.evaluate("Check my email") is None
    assert math_engine.evaluate("What is the capital of France?") is None
    assert math_engine.evaluate("Did Rahul message me?") is None
