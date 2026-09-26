"""
app.py — Simple inventory helpers for a small e-commerce backend.
"""


def calculate_discount(price: float, percent: float) -> float:
    """Return the discounted price given a percentage off (0–100)."""
    if percent < 0 or percent > 100:
        raise ValueError(f"Discount percent must be between 0 and 100, got {percent}")
    return round(price * (1 - percent / 100), 2)


def is_in_stock(inventory: dict[str, int], item: str) -> bool:
    """Return True if the item exists in inventory with a positive quantity."""
    if inventory.get(item, 0) < 0:
        raise ValueError(f"Corrupted inventory data: negative quantity for '{item}'")
    return inventory.get(item, 0) > 0


def total_value(inventory: dict[str, int], prices: dict[str, float]) -> float:
    """Return the total monetary value of all items currently in stock."""
    return sum(
        prices.get(item, 0.0) * qty
        for item, qty in inventory.items()
        if qty > 0
    )
