from dataclasses import dataclass


@dataclass(frozen=True)
class Cafe:
    """Local cafe record used by the mock Places data source."""

    id: str
    name: str
    category: str
    location: str
    address: str
    rating: float
    price: str
    description: str
    opening_hours: str
    amenities: tuple[str, ...]
    reviews: tuple[dict[str, str], ...]
    latitude: float | None = None
    longitude: float | None = None
