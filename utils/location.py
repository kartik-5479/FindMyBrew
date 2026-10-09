from __future__ import annotations

import re
from difflib import SequenceMatcher

from database.models import SearchIntent


CATEGORY_ALIASES = {
    "coffee": "Coffee",
    "coffee shop": "Coffee",
    "brew": "Coffee",
    "espresso": "Coffee",
    "cafe": "Cafe",
    "cafes": "Cafe",
    "bakery": "Cafe",
    "restaurant": "Restaurant",
    "restaurants": "Restaurant",
    "food": "Restaurant",
    "family restaurant": "Restaurant",
    "lounge": "Lounge",
    "lounges": "Lounge",
    "late night": "Lounge",
}

LOCATION_ALIASES = {
    "chd": "chandigarh",
    "sector-17": "sector 17",
    "sec 17": "sector 17",
    "sector-22": "sector 22",
    "sec 22": "sector 22",
    "sector-35": "sector 35",
    "sec 35": "sector 35",
    "sector-26": "sector 26",
    "sec 26": "sector 26",
    "sector-10": "sector 10",
    "sec 10": "sector 10",
    "elante mall": "elante",
    "elante area": "elante",
    "mohali phase 7": "phase 7 mohali",
    "vip road zirakpur": "vip road zirakpur",
}

KNOWN_REGION_TERMS = {
    "chandigarh",
    "mohali",
    "panchkula",
    "zirakpur",
    "patiala",
    "rajpura",
    "ludhiana",
    "model town",
    "sector 17",
    "sector 22",
    "sector 35",
    "sector 26",
    "sector 10",
    "sector 8",
    "phase 7",
    "elante",
    "vip road",
}

PURPOSE_WORDS = {
    "study": "studying",
    "studying": "studying",
    "work": "working",
    "working": "working",
    "date": "date",
    "family": "family",
    "friends": "friends",
    "meeting": "meeting",
}

AMBIENCE_WORDS = {
    "quiet",
    "cozy",
    "cosy",
    "late",
    "night",
    "rooftop",
    "outdoor",
    "pet",
    "wifi",
    "wi-fi",
    "work",
    "study",
    "family",
    "cheap",
    "budget",
    "premium",
    "date",
    "healthy",
    "vegan",
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "around",
    "at",
    "best",
    "find",
    "for",
    "in",
    "me",
    "near",
    "nearby",
    "next",
    "please",
    "shop",
    "show",
    "the",
    "to",
}


def normalize_text(value: str) -> str:
    text = value.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return LOCATION_ALIASES.get(text, text)


def tokens(value: str) -> tuple[str, ...]:
    return tuple(token for token in normalize_text(value).split() if token and token not in STOP_WORDS)


def detect_category(query: str, default: str = "All") -> str:
    normalized = normalize_text(query)
    for phrase, category in sorted(CATEGORY_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase in normalized:
            return category
    return default


def extract_location(query: str, explicit_location: str = "") -> str:
    if explicit_location.strip():
        return normalize_location(explicit_location)

    normalized = normalize_text(query)
    for prefix in (" near ", " in ", " at ", " around "):
        if prefix in f" {normalized} ":
            candidate = f" {normalized} ".split(prefix, 1)[1].strip()
            cleaned = " ".join(token for token in candidate.split() if token not in CATEGORY_ALIASES and token not in STOP_WORDS)
            if cleaned:
                return normalize_location(cleaned)

    for known_location in sorted(KNOWN_REGION_TERMS, key=len, reverse=True):
        if known_location in normalized:
            return normalize_location(known_location)
    return ""


def normalize_location(location: str) -> str:
    normalized = normalize_text(location)
    return LOCATION_ALIASES.get(normalized, normalized)


def parse_search_intent(query: str = "", explicit_location: str = "", category: str = "All") -> SearchIntent:
    raw_query = query.strip()
    combined = f"{raw_query} {explicit_location}".strip()
    selected_category = category if category != "All" else detect_category(combined, "All")
    budget = "budget" if any(word in normalize_text(combined) for word in ("cheap", "budget", "affordable")) else ""
    ambience = tuple(word for word in AMBIENCE_WORDS if word in normalize_text(combined))
    purpose = next((purpose for word, purpose in PURPOSE_WORDS.items() if word in normalize_text(combined)), "")
    useful_keywords = tuple(token for token in tokens(combined) if token not in tokens(selected_category))

    return SearchIntent(
        raw_query=raw_query,
        location=extract_location(raw_query, explicit_location),
        category=selected_category,
        budget=budget,
        ambience=ambience,
        purpose=purpose,
        keywords=useful_keywords,
    )


def location_score(query: str, haystack: str) -> float:
    normalized_query = normalize_location(query)
    normalized_haystack = normalize_text(haystack)
    if not normalized_query:
        return 1.0
    if normalized_query in normalized_haystack:
        return 1.0

    query_tokens = set(tokens(normalized_query))
    haystack_tokens = set(tokens(normalized_haystack))
    if not query_tokens:
        return 0.0

    overlap = len(query_tokens & haystack_tokens) / len(query_tokens)
    fuzzy = max((SequenceMatcher(None, token, candidate).ratio() for token in query_tokens for candidate in haystack_tokens), default=0.0)
    return max(overlap, fuzzy * 0.75)


def is_regionally_relevant(requested_location: str, cafe_location: str) -> bool:
    requested = normalize_location(requested_location)
    cafe = normalize_text(cafe_location)
    if not requested:
        return True
    if requested in cafe:
        return True

    tricity_terms = {"chandigarh", "mohali", "panchkula", "zirakpur", "patiala", "rajpura", "ludhiana"}
    return requested in tricity_terms and any(term in cafe for term in ("chandigarh", "mohali", "panchkula", "zirakpur"))
