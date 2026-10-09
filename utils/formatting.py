from __future__ import annotations


def price_level(price: str) -> str:
    text = price.lower()
    if any(value in text for value in ("450", "500")):
        return "Budget"
    if any(value in text for value in ("900", "1200")):
        return "Premium"
    return "Moderate"
