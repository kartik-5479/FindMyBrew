from __future__ import annotations

from database.models import Cafe


def has_coordinates(cafe: Cafe) -> bool:
    return cafe.latitude is not None and cafe.longitude is not None


def coordinates_label(cafe: Cafe) -> str:
    if not has_coordinates(cafe):
        return "Location coordinates unavailable"
    return f"{cafe.latitude:.4f}, {cafe.longitude:.4f}"
