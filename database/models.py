from dataclasses import dataclass, field


@dataclass(frozen=True)
class Cafe:
    """Normalized cafe/place object used across providers and UI."""

    id: str
    name: str
    category: str
    location: str
    address: str
    rating: float | None
    price: str
    description: str
    opening_hours: str
    amenities: tuple[str, ...]
    reviews: tuple[dict[str, str], ...]
    image_url: str = ""
    latitude: float | None = None
    longitude: float | None = None
    review_count: int | None = None
    is_open: bool | None = None
    phone: str = ""
    website: str = ""
    directions_url: str = ""
    photo_name: str = ""
    photo_attributions: tuple[str, ...] = ()
    distance_meters: float | None = None


@dataclass(frozen=True)
class SearchIntent:
    """Useful filters extracted from user-entered search text."""

    raw_query: str = ""
    location: str = ""
    category: str = "All"
    budget: str = ""
    ambience: tuple[str, ...] = ()
    purpose: str = ""
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchResult:
    """Cafe discovery result with explicit fallback context."""

    cafes: list[Cafe]
    exact_location: bool = True
    normalized_location: str = ""
    requested_location: str = ""
    message: str = ""
    alternatives: list[Cafe] = field(default_factory=list)
