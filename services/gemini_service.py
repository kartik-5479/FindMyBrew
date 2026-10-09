from __future__ import annotations

import json
import os
import re
from typing import Any

from database.models import Cafe, SearchIntent, SearchResult
from services.recommendation_service import build_reason, fallback_recommendations
from utils.location import normalize_location

MODEL_NAME = "gemini-3.8-flash"


def _load_environment() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def is_gemini_configured() -> bool:
    _load_environment()
    return bool(os.getenv("GEMINI_API_KEY"))


def _client():
    from google import genai
    from google.genai import types

    return genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(timeout=15_000),
    )


def _friendly_gemini_error(error: Exception) -> str:
    text = str(error).lower()
    if "resource_exhausted" in text or "quota" in text or "429" in text:
        return "Gemini search quota is exhausted right now. Try again later or add GOOGLE_MAPS_API_KEY for structured Places search."
    if "api_key" in text or "permission" in text or "401" in text or "403" in text:
        return "Gemini could not authorize this search. Check GEMINI_API_KEY in .env."
    if "not_found" in text or "404" in text:
        return "The configured Gemini model is unavailable. Update the model name or SDK before searching again."
    return "Google Maps search is temporarily unavailable. Check the Gemini key and try again."


def search_with_google_maps(intent: SearchIntent) -> SearchResult:
    """Use Gemini's Google Maps grounding; only grounded Maps chunks become places."""
    _load_environment()
    if not os.getenv("GEMINI_API_KEY"):
        return SearchResult(cafes=[], message="Add GEMINI_API_KEY to .env, or configure Google Places API (New), to search real places.")

    query_parts = [intent.raw_query.strip()]
    if intent.location and intent.location.casefold() not in intent.raw_query.casefold():
        query_parts.append(f"near {intent.location}")
    if not intent.raw_query:
        category = {
            "Coffee": "coffee shops",
            "Cafe": "cafes",
            "Restaurant": "restaurants",
            "Lounge": "lounges",
        }.get(intent.category, "cafes, coffee shops, restaurants, and lounges")
        query_parts.insert(0, category)
    query = " ".join(part for part in query_parts if part).strip()
    if not query:
        return SearchResult(cafes=[], message="Enter a city, neighborhood, or landmark to discover nearby places.")

    try:
        from google.genai import types

        client = _client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=(
                "Find real cafes, coffee shops, restaurants, or lounges for this request using Google Maps. "
                "Return a concise answer and use Google Maps grounding. Do not provide details unless supported by Maps.\n"
                f"Request: {query}"
            ),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps())],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
        candidates = getattr(response, "candidates", None) or []
        metadata = getattr(candidates[0], "grounding_metadata", None) if candidates else None
        chunks = getattr(metadata, "grounding_chunks", None) or []
        cafes: list[Cafe] = []
        seen: set[str] = set()
        for chunk in chunks:
            maps_data = getattr(chunk, "maps", None)
            place_id = getattr(maps_data, "place_id", None)
            name = (getattr(maps_data, "title", None) or "").strip()
            if not place_id or not name or place_id in seen:
                continue
            seen.add(place_id)
            cafes.append(Cafe(
                id=f"google:{place_id}",
                name=name,
                category=intent.category if intent.category != "All" else "Place",
                location="",
                address="",
                rating=None,
                price="",
                description="",
                opening_hours="",
                amenities=(),
                reviews=(),
                directions_url=getattr(maps_data, "uri", "") or "",
            ))
        if not cafes:
            message = "Google Maps could not verify places for that search. Try a nearby city, neighborhood, or landmark."
        else:
            message = "Places verified through Gemini Grounding with Google Maps. Ratings, hours, and photos appear only when separately available."
        return SearchResult(
            cafes=cafes,
            exact_location=bool(cafes),
            normalized_location=normalize_location(intent.location),
            requested_location=intent.location,
            message=message,
        )
    except Exception as error:
        return SearchResult(
            cafes=[],
            exact_location=False,
            requested_location=intent.location,
            message=_friendly_gemini_error(error),
        )


def _candidate_payload(cafes: list[Cafe]) -> list[dict[str, Any]]:
    payload = []
    for cafe in cafes:
        item: dict[str, Any] = {"id": cafe.id, "name": cafe.name, "category": cafe.category}
        verified_fields = {
            "location": cafe.location,
            "address": cafe.address,
            "rating": cafe.rating,
            "price_level": cafe.price,
            "description": cafe.description,
            "opening_hours": cafe.opening_hours,
            "amenities": list(cafe.amenities),
            "reviews": list(cafe.reviews),
        }
        item.update({key: value for key, value in verified_fields.items() if value not in (None, "", [], ())})
        payload.append(item)
    return payload


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def get_ai_recommendations(
    cafes: list[Cafe], intent: SearchIntent, enabled: bool = True
) -> tuple[list[dict[str, str]], str]:
    if not cafes:
        return [], "No verified places are available to recommend."
    if not enabled:
        return fallback_recommendations(cafes, intent), "AI is disabled in Settings; showing local matches."
    if not is_gemini_configured():
        return fallback_recommendations(cafes, intent), "Add GEMINI_API_KEY for AI ranking; showing local matches for now."

    try:
        from google.genai import types

        prompt = {
            "task": "Rank these real places for the user's request.",
            "rules": [
                "Use only supplied place facts. Never infer or invent an amenity, review, rating, address, price, or opening hour.",
                "Return JSON only with key recommendations, an array of cafe_id values in preference order.",
                "Only select ids from the supplied candidate list.",
            ],
            "intent": {
                "query": intent.raw_query,
                "location": intent.location,
                "category": intent.category,
                "budget": intent.budget,
                "ambience": list(intent.ambience),
                "purpose": intent.purpose,
            },
            "candidates": _candidate_payload(cafes),
        }
        client = _client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=json.dumps(prompt),
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        parsed = _parse_json(getattr(response, "text", "") or "{}")
        items = parsed.get("recommendations", []) if isinstance(parsed, dict) else []
        allowed = {cafe.id: cafe for cafe in cafes}
        seen: set[str] = set()
        ranked: list[dict[str, str]] = []
        for item in items:
            cafe_id = item.get("cafe_id", "") if isinstance(item, dict) else item
            if cafe_id in allowed and cafe_id not in seen:
                ranked.append({"cafe_id": cafe_id, "reason": build_reason(allowed[cafe_id], intent)})
                seen.add(cafe_id)
        if ranked:
            return ranked[:4], "Ranked by Gemini using verified place information."
    except Exception:
        pass
    return fallback_recommendations(cafes, intent), "Gemini is unavailable; showing local matches based on verified information."


def get_ai_vibe(cafe: Cafe) -> str:
    """Return a clearly inferred ambience only when verified text is available."""
    verified_text = " ".join((cafe.description, " ".join(cafe.amenities), " ".join(review.get("text", "") for review in cafe.reviews))).strip()
    if not verified_text or not is_gemini_configured():
        return "Not enough verified place information for an AI vibe summary."
    try:
        prompt = (
            "In one short sentence, cautiously interpret the likely ambience from only the supplied verified description, "
            "amenities, and review excerpts. Do not add factual claims or amenities. This is an inference, not a fact.\n"
            + json.dumps({"name": cafe.name, "description": cafe.description, "amenities": cafe.amenities, "reviews": cafe.reviews})
        )
        client = _client()
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = (getattr(response, "text", "") or "").strip()
        return text[:360] if text else "Not enough verified place information for an AI vibe summary."
    except Exception:
        return "AI vibe interpretation is temporarily unavailable."
