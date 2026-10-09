from __future__ import annotations

from database.models import Cafe


def get_reviews(cafe: Cafe) -> tuple[dict[str, str], ...]:
    return cafe.reviews or ()


def has_reviews(cafe: Cafe) -> bool:
    return bool(cafe.reviews)
