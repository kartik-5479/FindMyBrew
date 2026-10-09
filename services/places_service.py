from __future__ import annotations

import json
import os
from pathlib import Path
from functools import lru_cache
from dataclasses import replace
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from database.models import Cafe, SearchIntent, SearchResult
from utils.location import is_regionally_relevant, location_score, normalize_location, parse_search_intent

FALLBACK_IMAGE_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "cafe-fallback.svg")
PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACE_FIELDS = ",".join((
    "places.id", "places.displayName", "places.primaryType", "places.types",
    "places.formattedAddress", "places.location", "places.rating",
    "places.userRatingCount", "places.priceLevel", "places.currentOpeningHours",
    "places.nationalPhoneNumber", "places.websiteUri", "places.googleMapsUri",
    "places.photos", "places.reviews",
))
PLACE_TYPE_BY_CATEGORY = {
    "Coffee": "coffee_shop",
    "Cafe": "cafe",
    "Restaurant": "restaurant",
    "Lounge": "bar",
}
PRICE_LEVELS = {
    "PRICE_LEVEL_FREE": "Free",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}


def _friendly_google_error(error: HTTPError) -> str:
    if error.code == 429:
        return "Google Places is receiving too many requests. Please try again shortly."
    if error.code in (401, 403):
        return "Google Places could not authorize this search. Check GOOGLE_MAPS_API_KEY and Places API access."
    if error.code == 400:
        return "Google Places could not understand that search. Try a nearby city, neighborhood, or landmark."
    return "Google Places could not complete the search right now."


def _load_environment() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def _place_category(place: dict, requested: str) -> str:
    if requested != "All":
        return requested
    types = [place.get("primaryType", ""), *place.get("types", [])]
    for place_type, category in (("coffee_shop", "Coffee"), ("cafe", "Cafe"), ("restaurant", "Restaurant"), ("bar", "Lounge")):
        if place_type in types:
            return category
    return "Place"


def _normalize_place(place: dict, intent: SearchIntent) -> Cafe | None:
    place_id = place.get("id")
    name = (place.get("displayName") or {}).get("text", "").strip()
    if not place_id or not name:
        return None

    location = place.get("location") or {}
    opening = place.get("currentOpeningHours") or {}
    photo = next(iter(place.get("photos") or []), {})
    reviews = []
    for review in place.get("reviews") or []:
        author = (review.get("authorAttribution") or {}).get("displayName", "")
        text = (review.get("text") or {}).get("text", "")
        rating = review.get("rating")
        if author or text:
            reviews.append({"author": author, "rating": str(rating) if rating is not None else "", "text": text})

    return Cafe(
        id=f"google:{place_id}",
        name=name,
        category=_place_category(place, intent.category),
        location=place.get("formattedAddress", ""),
        address=place.get("formattedAddress", ""),
        rating=place.get("rating"),
        price=PRICE_LEVELS.get(place.get("priceLevel", ""), ""),
        description="",
        opening_hours="\n".join(opening.get("weekdayDescriptions", [])),
        amenities=(),
        reviews=tuple(reviews),
        latitude=(location.get("latitude")),
        longitude=(location.get("longitude")),
        review_count=place.get("userRatingCount"),
        is_open=opening.get("openNow"),
        phone=place.get("nationalPhoneNumber", ""),
        website=place.get("websiteUri", ""),
        directions_url=place.get("googleMapsUri", ""),
        photo_name=photo.get("name", ""),
        photo_attributions=tuple(
            attribution.get("displayName", "")
            for attribution in photo.get("authorAttributions", [])
            if attribution.get("displayName")
        ),
    )


class GooglePlacesProvider:
    """Structured discovery using the current Google Places API (New)."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search(self, intent: SearchIntent) -> SearchResult:
        search_text = intent.raw_query.strip()
        if intent.location and intent.location.casefold() not in search_text.casefold():
            search_text = f"{search_text} near {intent.location}".strip()
        if not search_text:
            search_text = f"cafes and restaurants in {intent.location}" if intent.location else "cafes and restaurants"

        payload = {"textQuery": search_text, "pageSize": 20, "languageCode": "en"}
        place_type = PLACE_TYPE_BY_CATEGORY.get(intent.category)
        if place_type:
            payload["includedType"] = place_type
            payload["strictTypeFiltering"] = True
        request = Request(
            PLACES_SEARCH_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": PLACE_FIELDS,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            return SearchResult(cafes=[], exact_location=False, requested_location=intent.location, message=_friendly_google_error(error))
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            return SearchResult(cafes=[], exact_location=False, requested_location=intent.location, message="Place search is temporarily unavailable. Check your connection and try again.")

        cafes = [
            cafe for place in data.get("places", [])
            if (cafe := _normalize_place(place, intent)) is not None
        ]
        if not cafes:
            place = f" around {intent.location}" if intent.location else " for that search"
            message = f"No cafes or restaurants were found{place}. Try a nearby area or landmark."
        else:
            message = ""
        return SearchResult(
            cafes=cafes,
            exact_location=bool(cafes),
            normalized_location=normalize_location(intent.location),
            requested_location=intent.location,
            message=message,
        )


@lru_cache(maxsize=128)
def _fetch_place_photo(photo_name: str, api_key: str) -> bytes | None:
    url = f"https://places.googleapis.com/v1/{quote(photo_name, safe='/')}/media?maxWidthPx=1200&key={quote(api_key)}"
    request = Request(url, headers={"User-Agent": "FindMyBrew/1.0"})
    try:
        with urlopen(request, timeout=8) as response:
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                return None
            return response.read()
    except (HTTPError, URLError, TimeoutError, OSError):
        return None


def get_cafe_image(cafe: Cafe) -> bytes | str:
    """Return authentic provider photo bytes or a neutral generic fallback image."""
    _load_environment()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if cafe.photo_name and api_key:
        image = _fetch_place_photo(cafe.photo_name, api_key)
        if image:
            return image
    if cafe.id in SAMPLE_CAFE_IDS:
        return FALLBACK_IMAGE_PATH
    return cafe.image_url or FALLBACK_IMAGE_PATH


CAFE_DATA: tuple[Cafe, ...] = (
    Cafe(id="brew-room-sector-17", name="The Brew Room", category="Coffee", location="Sector 17, Chandigarh", address="SCO 12, Sector 17 Plaza, Chandigarh", rating=4.6, price="Rs. 600 for two", description="Specialty coffee, warm interiors, fresh bakes, and quiet corners for catch-ups.", opening_hours="8:00 AM - 11:00 PM", amenities=("Free Wi-Fi", "Outdoor seating", "Fresh bakery", "Work-friendly"), reviews=({"author": "Aarav", "rating": "5.0", "text": "Excellent pour-over and a calm morning vibe."}, {"author": "Meera", "rating": "4.5", "text": "The croissants and cold brew are both worth returning for."}), image_url="https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=80", latitude=30.7415, longitude=76.7681),
    Cafe(id="bean-theory-sector-35", name="Bean Theory", category="Cafe", location="Sector 35, Chandigarh", address="Booth 44, Sector 35 Market, Chandigarh", rating=4.4, price="Rs. 500 for two", description="A cozy neighborhood cafe with espresso classics, sandwiches, and soft lighting.", opening_hours="9:00 AM - 10:30 PM", amenities=("Pet friendly", "Board games", "Desserts", "Takeaway"), reviews=({"author": "Kabir", "rating": "4.4", "text": "Friendly staff and a reliable cappuccino."},), image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80", latitude=30.7209, longitude=76.7590),
    Cafe(id="roast-relax-elante", name="Roast & Relax", category="Lounge", location="Elante Area, Chandigarh", address="Industrial Area Phase 1, near Elante Mall, Chandigarh", rating=4.5, price="Rs. 900 for two", description="Freshly roasted coffee by day with a relaxed lounge menu in the evening.", opening_hours="10:00 AM - 12:00 AM", amenities=("Late night", "Lounge seating", "Mocktails", "Parking"), reviews=({"author": "Simran", "rating": "4.7", "text": "Great place for a slow evening after shopping."},), image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80", latitude=30.7056, longitude=76.8013),
    Cafe(id="cafe-chapter-sector-8", name="Cafe Chapter", category="Cafe", location="Sector 8, Chandigarh", address="SCO 21, Inner Market, Sector 8, Chandigarh", rating=4.3, price="Rs. 550 for two", description="Coffee, desserts, and a quiet space to read, work, or unwind.", opening_hours="8:30 AM - 10:00 PM", amenities=("Quiet tables", "Book corner", "Pastries", "Charging points"), reviews=({"author": "Nisha", "rating": "4.2", "text": "Peaceful, tidy, and very easy to work from."},), image_url="https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&w=1200&q=80", latitude=30.7462, longitude=76.7937),
    Cafe(id="urban-kettle-mohali", name="Urban Kettle", category="Coffee", location="Phase 7, Mohali", address="SCF 61, Phase 7 Market, Mohali", rating=4.7, price="Rs. 650 for two", description="Single-origin brews, hearty breakfast plates, and bright modern seating.", opening_hours="7:30 AM - 10:30 PM", amenities=("Breakfast", "Specialty beans", "Free Wi-Fi", "Vegan options"), reviews=({"author": "Riya", "rating": "4.8", "text": "Their iced latte is easily one of the best in town."},), image_url="https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=80", latitude=30.7046, longitude=76.7179),
    Cafe(id="terrace-beans-panchkula", name="Terrace Beans", category="Restaurant", location="Sector 5, Panchkula", address="Rooftop, Sector 5 Market, Panchkula", rating=4.2, price="Rs. 800 for two", description="An airy terrace spot serving cafe staples, pastas, pizzas, and coffee.", opening_hours="11:00 AM - 11:30 PM", amenities=("Rooftop", "Live music", "Family friendly", "Reservations"), reviews=({"author": "Dev", "rating": "4.1", "text": "Nice rooftop ambience and generous portions."},), image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=1200&q=80", latitude=30.6942, longitude=76.8606),
    Cafe(id="mocha-lane-sector-22", name="Mocha Lane", category="Coffee", location="Sector 22, Chandigarh", address="SCO 101, Sector 22 Market, Chandigarh", rating=4.1, price="Rs. 450 for two", description="Quick coffees, shakes, waffles, and a convenient central location.", opening_hours="9:00 AM - 11:00 PM", amenities=("Budget friendly", "Waffles", "Takeaway", "Student friendly"), reviews=(), image_url="https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80", latitude=30.7333, longitude=76.7794),
    Cafe(id="saffron-cup-zirakpur", name="Saffron Cup", category="Restaurant", location="VIP Road, Zirakpur", address="Ground Floor, VIP Road, Zirakpur", rating=4.0, price="Rs. 700 for two", description="Cafe-style comfort food with Indian plates, desserts, and classic coffees.", opening_hours="10:30 AM - 11:00 PM", amenities=("Indian menu", "Desserts", "Parking", "Family seating"), reviews=({"author": "Harleen", "rating": "4.0", "text": "Good food variety and quick service."},), image_url="https://images.unsplash.com/photo-1533777857889-4be7c70b33f7?auto=format&fit=crop&w=1200&q=80", latitude=30.6425, longitude=76.8173),
    Cafe(id="night-jar-lounge", name="Night Jar Lounge", category="Lounge", location="Sector 26, Chandigarh", address="SCO 33, Sector 26, Chandigarh", rating=4.5, price="Rs. 1200 for two", description="Dim lights, signature mocktails, small plates, and a refined late-evening feel.", opening_hours="12:00 PM - 1:00 AM", amenities=("Late night", "Small plates", "Reservations", "Ambient music"), reviews=({"author": "Ishaan", "rating": "4.6", "text": "Perfect for a relaxed late night plan."},), image_url="https://images.unsplash.com/photo-1572116469696-31de0f17cc34?auto=format&fit=crop&w=1200&q=80", latitude=30.7270, longitude=76.8090),
    Cafe(id="green-grind-sector-10", name="Green Grind", category="Cafe", location="Sector 10, Chandigarh", address="Booth 9, Sector 10, Chandigarh", rating=4.6, price="Rs. 750 for two", description="Plant-forward cafe with matcha, smoothie bowls, sandwiches, and specialty coffee.", opening_hours="8:00 AM - 9:30 PM", amenities=("Vegan options", "Healthy bowls", "Matcha", "Outdoor seating"), reviews=({"author": "Tara", "rating": "4.8", "text": "Fresh bowls and a very good oat milk latte."},), image_url="https://images.unsplash.com/photo-1525610553991-2bede1a236e2?auto=format&fit=crop&w=1200&q=80", latitude=30.7537, longitude=76.7873),
)

CATEGORIES = ("All", "Coffee", "Cafe", "Restaurant", "Lounge")
SAMPLE_CAFE_IDS = frozenset(cafe.id for cafe in CAFE_DATA)


class PlacesProvider(Protocol):
    def search(self, intent: SearchIntent) -> SearchResult:
        """Return normalized cafes for the supplied intent."""


class LocalPlacesProvider:
    """Offline provider backed by the bundled cafe dataset."""

    def __init__(self, cafes: tuple[Cafe, ...] = CAFE_DATA) -> None:
        self.cafes = cafes

    def search(self, intent: SearchIntent) -> SearchResult:
        category = intent.category if intent.category in CATEGORIES else "All"
        requested_location = intent.location
        normalized_location = normalize_location(requested_location)
        category_matches = [cafe for cafe in self.cafes if category == "All" or cafe.category == category]
        scored = [(cafe, location_score(normalized_location, f"{cafe.name} {cafe.location} {cafe.address}")) for cafe in category_matches]
        exact_matches = [cafe for cafe, score in scored if not normalized_location or score >= 0.55]

        if exact_matches:
            return SearchResult(cafes=sorted(exact_matches, key=lambda cafe: cafe.rating or 0, reverse=True), exact_location=True, normalized_location=normalized_location, requested_location=requested_location)

        alternatives = [cafe for cafe in category_matches if is_regionally_relevant(normalized_location, cafe.location)] or category_matches
        message = f"No local dataset cafes were found inside {requested_location}. Showing relevant available places from the broader Chandigarh region instead." if requested_location else "Showing popular available places from the local dataset."
        return SearchResult(cafes=[], exact_location=False, normalized_location=normalized_location, requested_location=requested_location, alternatives=sorted(alternatives, key=lambda cafe: cafe.rating or 0, reverse=True)[:6], message=message)


class GeminiMapsProvider:
    """Adapter for place references grounded by Gemini with Google Maps."""

    def search(self, intent: SearchIntent) -> SearchResult:
        from services.gemini_service import search_with_google_maps

        return search_with_google_maps(intent)


class UnavailablePlacesProvider:
    def search(self, intent: SearchIntent) -> SearchResult:
        return SearchResult(
            cafes=[],
            exact_location=False,
            requested_location=intent.location,
            message="Real place search needs GEMINI_API_KEY for Google Maps grounding or GOOGLE_MAPS_API_KEY for Places API (New).",
        )


class PlacesService:
    """Coordinate real providers, with bundled sample data available only by opt-in."""

    def __init__(self, providers: list[PlacesProvider] | None = None) -> None:
        if providers is not None:
            self.providers = providers
            return
        _load_environment()
        self.providers = []
        maps_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        if maps_key:
            self.providers.append(GooglePlacesProvider(maps_key))
        if os.getenv("GEMINI_API_KEY"):
            self.providers.append(GeminiMapsProvider())
        if os.getenv("FINDBREW_USE_MOCK_DATA", "").lower() in {"1", "true", "yes"}:
            self.providers.append(LocalPlacesProvider())
        if not self.providers:
            self.providers.append(UnavailablePlacesProvider())

    def discover(self, intent: SearchIntent) -> SearchResult:
        if not intent.location and not intent.raw_query.strip():
            return SearchResult(cafes=[], message="Enter a city, neighborhood, or landmark to search real places.")
        if not intent.location and any(term in intent.raw_query.casefold() for term in ("near me", "nearby", "around me")):
            return SearchResult(cafes=[], message="Add a city, neighborhood, or landmark for nearby results. FindMyBrew does not access your device location.")
        last_result: SearchResult | None = None
        for provider in self.providers:
            result = provider.search(intent)
            if result.cafes:
                return result
            last_result = result
        return last_result or SearchResult(cafes=[])


def with_image_fallback(cafe: Cafe) -> Cafe:
    if cafe.id in SAMPLE_CAFE_IDS:
        return replace(cafe, image_url=FALLBACK_IMAGE_PATH)
    return cafe if cafe.image_url else replace(cafe, image_url=FALLBACK_IMAGE_PATH)


def get_all_cafes() -> list[Cafe]:
    return [with_image_fallback(cafe) for cafe in CAFE_DATA]


def get_cafe_by_id(cafe_id: str | None) -> Cafe | None:
    if not cafe_id:
        return None
    cafe = _CAFE_CACHE.get(cafe_id) or next((item for item in CAFE_DATA if item.id == cafe_id), None)
    return with_image_fallback(cafe) if cafe else None


def discover_cafes(query: str = "", location: str = "", category: str = "All") -> tuple[SearchIntent, SearchResult]:
    intent = parse_search_intent(query=query, explicit_location=location, category=category)
    result = PlacesService().discover(intent)
    _CAFE_CACHE.update({cafe.id: cafe for cafe in (*result.cafes, *result.alternatives)})
    return intent, result


def search_cafes(location: str = "", category: str = "All", query: str = "") -> list[Cafe]:
    _intent, result = discover_cafes(query=query, location=location, category=category)
    return result.cafes or result.alternatives


def get_popular_cafes(limit: int = 4) -> list[Cafe]:
    _load_environment()
    if os.getenv("FINDBREW_USE_MOCK_DATA", "").lower() not in {"1", "true", "yes"}:
        return []
    return sorted(get_all_cafes(), key=lambda item: item.rating or 0, reverse=True)[:limit]


_CAFE_CACHE: dict[str, Cafe] = {cafe.id: cafe for cafe in CAFE_DATA}
