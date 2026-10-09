from __future__ import annotations

from database.models import Cafe, SearchIntent


def _text_for(cafe: Cafe) -> str:
    return " ".join((cafe.category, cafe.location, cafe.description, " ".join(cafe.amenities))).lower()


def score_cafe(cafe: Cafe, intent: SearchIntent) -> float:
    text = _text_for(cafe)
    score = cafe.rating or 0.0

    for keyword in intent.keywords:
        if keyword.lower() in text or keyword.lower() in cafe.name.lower():
            score += 0.35
    for ambience in intent.ambience:
        if ambience in text:
            score += 0.55
    if intent.purpose and intent.purpose in text:
        score += 0.45
    if intent.budget and any(word in text for word in ("budget", "student", "affordable")):
        score += 0.6
    if intent.category != "All" and cafe.category == intent.category:
        score += 0.5

    return score


def fallback_recommendations(cafes: list[Cafe], intent: SearchIntent, limit: int = 4) -> list[dict[str, str]]:
    ranked = sorted(cafes, key=lambda cafe: score_cafe(cafe, intent), reverse=True)[:limit]
    return [{"cafe_id": cafe.id, "reason": build_reason(cafe, intent)} for cafe in ranked]


def build_reason(cafe: Cafe, intent: SearchIntent) -> str:
    reasons = []
    amenities = ", ".join(cafe.amenities[:2])
    if amenities:
        reasons.append(f"offers {amenities}")
    if intent.budget and any("budget" in item.lower() or "student" in item.lower() for item in cafe.amenities):
        reasons.append("fits a budget-friendly search")
    if intent.purpose and intent.purpose in _text_for(cafe):
        reasons.append(f"matches a {intent.purpose} plan")
    if not reasons and cafe.rating is not None:
        reasons.append(f"has a strong {cafe.rating:.1f} rating")
    if not reasons:
        reasons.append("matches your search preferences")
    return "Recommended because it " + " and ".join(reasons) + "."


def hydrate_recommendations(cafes: list[Cafe], recommendations: list[dict[str, str]]) -> list[tuple[Cafe, str]]:
    by_id = {cafe.id: cafe for cafe in cafes}
    hydrated = []
    seen = set()
    for item in recommendations:
        cafe_id = item.get("cafe_id", "")
        if cafe_id in by_id and cafe_id not in seen:
            hydrated.append((by_id[cafe_id], item.get("reason", "Recommended from available cafe data.")))
            seen.add(cafe_id)
    return hydrated
