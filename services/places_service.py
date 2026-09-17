from database.models import Cafe


CAFE_DATA: tuple[Cafe, ...] = (
    Cafe(
        id="brew-room-sector-17",
        name="The Brew Room",
        category="Coffee",
        location="Sector 17, Chandigarh",
        address="SCO 12, Sector 17 Plaza, Chandigarh",
        rating=4.6,
        price="Rs. 600 for two",
        description="Specialty coffee, warm interiors, fresh bakes, and quiet corners for catch-ups.",
        opening_hours="8:00 AM - 11:00 PM",
        amenities=("Free Wi-Fi", "Outdoor seating", "Fresh bakery", "Work-friendly"),
        reviews=(
            {"author": "Aarav", "rating": "5.0", "text": "Excellent pour-over and a calm morning vibe."},
            {"author": "Meera", "rating": "4.5", "text": "The croissants and cold brew are both worth returning for."},
        ),
        latitude=30.7415,
        longitude=76.7681,
    ),
    Cafe(
        id="bean-theory-sector-35",
        name="Bean Theory",
        category="Cafe",
        location="Sector 35, Chandigarh",
        address="Booth 44, Sector 35 Market, Chandigarh",
        rating=4.4,
        price="Rs. 500 for two",
        description="A cozy neighborhood cafe with espresso classics, sandwiches, and soft lighting.",
        opening_hours="9:00 AM - 10:30 PM",
        amenities=("Pet friendly", "Board games", "Desserts", "Takeaway"),
        reviews=({"author": "Kabir", "rating": "4.4", "text": "Friendly staff and a reliable cappuccino."},),
        latitude=30.7209,
        longitude=76.7590,
    ),
    Cafe(
        id="roast-relax-elante",
        name="Roast & Relax",
        category="Lounge",
        location="Elante Area, Chandigarh",
        address="Industrial Area Phase 1, near Elante Mall, Chandigarh",
        rating=4.5,
        price="Rs. 900 for two",
        description="Freshly roasted coffee by day with a relaxed lounge menu in the evening.",
        opening_hours="10:00 AM - 12:00 AM",
        amenities=("Late night", "Lounge seating", "Mocktails", "Parking"),
        reviews=({"author": "Simran", "rating": "4.7", "text": "Great place for a slow evening after shopping."},),
        latitude=30.7056,
        longitude=76.8013,
    ),
    Cafe(
        id="cafe-chapter-sector-8",
        name="Cafe Chapter",
        category="Cafe",
        location="Sector 8, Chandigarh",
        address="SCO 21, Inner Market, Sector 8, Chandigarh",
        rating=4.3,
        price="Rs. 550 for two",
        description="Coffee, desserts, and a quiet space to read, work, or unwind.",
        opening_hours="8:30 AM - 10:00 PM",
        amenities=("Quiet tables", "Book corner", "Pastries", "Charging points"),
        reviews=({"author": "Nisha", "rating": "4.2", "text": "Peaceful, tidy, and very easy to work from."},),
        latitude=30.7462,
        longitude=76.7937,
    ),
    Cafe(
        id="urban-kettle-mohali",
        name="Urban Kettle",
        category="Coffee",
        location="Phase 7, Mohali",
        address="SCF 61, Phase 7 Market, Mohali",
        rating=4.7,
        price="Rs. 650 for two",
        description="Single-origin brews, hearty breakfast plates, and bright modern seating.",
        opening_hours="7:30 AM - 10:30 PM",
        amenities=("Breakfast", "Specialty beans", "Free Wi-Fi", "Vegan options"),
        reviews=({"author": "Riya", "rating": "4.8", "text": "Their iced latte is easily one of the best in town."},),
        latitude=30.7046,
        longitude=76.7179,
    ),
    Cafe(
        id="terrace-beans-panchkula",
        name="Terrace Beans",
        category="Restaurant",
        location="Sector 5, Panchkula",
        address="Rooftop, Sector 5 Market, Panchkula",
        rating=4.2,
        price="Rs. 800 for two",
        description="An airy terrace spot serving cafe staples, pastas, pizzas, and coffee.",
        opening_hours="11:00 AM - 11:30 PM",
        amenities=("Rooftop", "Live music", "Family friendly", "Reservations"),
        reviews=({"author": "Dev", "rating": "4.1", "text": "Nice rooftop ambience and generous portions."},),
        latitude=30.6942,
        longitude=76.8606,
    ),
    Cafe(
        id="mocha-lane-sector-22",
        name="Mocha Lane",
        category="Coffee",
        location="Sector 22, Chandigarh",
        address="SCO 101, Sector 22 Market, Chandigarh",
        rating=4.1,
        price="Rs. 450 for two",
        description="Quick coffees, shakes, waffles, and a convenient central location.",
        opening_hours="9:00 AM - 11:00 PM",
        amenities=("Budget friendly", "Waffles", "Takeaway", "Student friendly"),
        reviews=(),
        latitude=30.7333,
        longitude=76.7794,
    ),
    Cafe(
        id="saffron-cup-zirakpur",
        name="Saffron Cup",
        category="Restaurant",
        location="VIP Road, Zirakpur",
        address="Ground Floor, VIP Road, Zirakpur",
        rating=4.0,
        price="Rs. 700 for two",
        description="Cafe-style comfort food with Indian plates, desserts, and classic coffees.",
        opening_hours="10:30 AM - 11:00 PM",
        amenities=("Indian menu", "Desserts", "Parking", "Family seating"),
        reviews=({"author": "Harleen", "rating": "4.0", "text": "Good food variety and quick service."},),
        latitude=30.6425,
        longitude=76.8173,
    ),
    Cafe(
        id="night-jar-lounge",
        name="Night Jar Lounge",
        category="Lounge",
        location="Sector 26, Chandigarh",
        address="SCO 33, Sector 26, Chandigarh",
        rating=4.5,
        price="Rs. 1200 for two",
        description="Dim lights, signature mocktails, small plates, and a refined late-evening feel.",
        opening_hours="12:00 PM - 1:00 AM",
        amenities=("Late night", "Small plates", "Reservations", "Ambient music"),
        reviews=({"author": "Ishaan", "rating": "4.6", "text": "Perfect for a relaxed late night plan."},),
        latitude=30.7270,
        longitude=76.8090,
    ),
    Cafe(
        id="green-grind-sector-10",
        name="Green Grind",
        category="Cafe",
        location="Sector 10, Chandigarh",
        address="Booth 9, Sector 10, Chandigarh",
        rating=4.6,
        price="Rs. 750 for two",
        description="Plant-forward cafe with matcha, smoothie bowls, sandwiches, and specialty coffee.",
        opening_hours="8:00 AM - 9:30 PM",
        amenities=("Vegan options", "Healthy bowls", "Matcha", "Outdoor seating"),
        reviews=({"author": "Tara", "rating": "4.8", "text": "Fresh bowls and a very good oat milk latte."},),
        latitude=30.7537,
        longitude=76.7873,
    ),
)

CATEGORIES = ("All", "Coffee", "Cafe", "Restaurant", "Lounge")


def get_all_cafes() -> list[Cafe]:
    return list(CAFE_DATA)


def get_cafe_by_id(cafe_id: str | None) -> Cafe | None:
    if not cafe_id:
        return None
    return next((cafe for cafe in CAFE_DATA if cafe.id == cafe_id), None)


def search_cafes(location: str = "", category: str = "All") -> list[Cafe]:
    location_query = location.strip().lower()
    category_query = category if category in CATEGORIES else "All"

    results = []
    for cafe in CAFE_DATA:
        matches_category = category_query == "All" or cafe.category == category_query
        matches_location = (
            not location_query
            or location_query in cafe.location.lower()
            or location_query in cafe.address.lower()
            or location_query in cafe.name.lower()
        )
        if matches_category and matches_location:
            results.append(cafe)

    return sorted(results, key=lambda item: item.rating, reverse=True)


def get_popular_cafes(limit: int = 4) -> list[Cafe]:
    return sorted(CAFE_DATA, key=lambda item: item.rating, reverse=True)[:limit]
