# FindMyBrew

FindMyBrew is a Streamlit cafe discovery app for finding nearby coffee shops, cafes, restaurants, and lounges. It uses a local mock Places dataset, so the app runs without API keys while keeping the service layer ready for a future real Places API integration.

## Features

- Cream/orange cafe-themed Streamlit UI
- Session-state page routing for Home, Search, Favorites, Settings, and Cafe Details
- Location search with category filters
- Dynamic result counts and empty states
- Cafe cards with details and favorite/unfavorite actions
- Cafe detail pages with address, hours, amenities, reviews, and map preview data
- Session-backed favorites using stable cafe IDs
- Settings for default location, default category, ratings visibility, and prices visibility

## Tech Stack

- Python
- Streamlit
- HTML/CSS through Streamlit markdown
- Local mock data service
- Session-state persistence

## Project Structure

```text
FindMyBrew/
  app.py
  components/
    cafe_card.py
    filter_panel.py
    footer.py
    map_view.py
    navbar.py
    review_card.py
  database/
    database.py
    models.py
  pages/
    cafe_details.py
    favorites.py
    home.py
    search.py
    settings.py
  services/
    places_service.py
  styles/
    main.css
  requirements.txt
  README.md
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Live Demo

Live Streamlit demo: _Add deployed Streamlit URL here._
