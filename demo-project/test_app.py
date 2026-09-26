"""
test_app.py — Basic pytest tests for app.py.
"""

import pytest
from app import calculate_discount, is_in_stock, total_value


# ---------------------------------------------------------------------------
# calculate_discount
# ---------------------------------------------------------------------------

def test_calculate_discount_ten_percent():
    assert calculate_discount(100.0, 10) == 90.0


def test_calculate_discount_zero_percent():
    assert calculate_discount(50.0, 0) == 50.0


def test_calculate_discount_full():
    assert calculate_discount(80.0, 100) == 0.0


def test_calculate_discount_invalid_raises():
    with pytest.raises(ValueError):
        calculate_discount(100.0, -5)

    with pytest.raises(ValueError):
        calculate_discount(100.0, 110)


# ---------------------------------------------------------------------------
# is_in_stock
# ---------------------------------------------------------------------------

def test_is_in_stock_present():
    assert is_in_stock({"widget": 3, "gadget": 0}, "widget") is True


def test_is_in_stock_zero_quantity():
    assert is_in_stock({"widget": 0}, "widget") is False


def test_is_in_stock_missing_item():
    assert is_in_stock({}, "widget") is False


# ---------------------------------------------------------------------------
# total_value
# ---------------------------------------------------------------------------

def test_total_value_basic():
    inventory = {"widget": 2, "gadget": 5}
    prices = {"widget": 9.99, "gadget": 4.50}
    assert total_value(inventory, prices) == pytest.approx(2 * 9.99 + 5 * 4.50)


def test_total_value_skips_out_of_stock():
    inventory = {"widget": 1, "gadget": 0}
    prices = {"widget": 10.0, "gadget": 5.0}
    assert total_value(inventory, prices) == 10.0


def test_total_value_empty_inventory():
    assert total_value({}, {"widget": 9.99}) == 0.0
