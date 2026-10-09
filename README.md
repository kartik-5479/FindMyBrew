# FindMyBrew

FindMyBrew is a Streamlit discovery app for real cafes, coffee shops, restaurants, and lounges. Search by city, town, neighborhood, area, landmark, or natural-language intent, then save places and inspect verified details.

## Features

- Home, Search, Favorites, Settings, and Cafe Details pages
- Search by city, small town, neighborhood, sector, local area, or landmark
- Natural-language prompts such as `quiet cafe for studying` and `romantic cafe with desserts`
- Category filters for Coffee, Cafe, Restaurant, and Lounge
- Optional Google Places API (New) integration for structured ratings, hours, contact details, reviews, and Place Photos
- Gemini AI recommendations and vibe summaries that use only verified place information supplied by providers
- Friendly fallback states for missing keys, no results, provider errors, network failures, and missing images
- Session-backed favorites and preferences

## Discovery Providers

- Google Places API (New) is preferred when `GOOGLE_MAPS_API_KEY` is configured.
- Gemini Grounding with Google Maps uses `GEMINI_API_KEY` to return real Maps-grounded place references when structured Places search is unavailable.
- Missing fields stay missing. FindMyBrew does not invent ratings, prices, addresses, amenities, reviews, hours, or cafe-specific photos.
- When Gemini is unavailable, verified place results continue to display and deterministic local matching is used for recommendation order.
- AI-generated ambience is clearly labeled as an inference.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your keys to `.env`:

```env
GEMINI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
FINDBREW_USE_MOCK_DATA=false
```

`GOOGLE_MAPS_API_KEY` is optional, but it enables richer structured place data and provider photos. Enable Places API (New) for that Google Cloud project and restrict API keys to the APIs the app needs. Keep `.env` out of version control.

## Run

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Development Sample Data

Bundled sample records are not used for production searches. To preview the UI offline, opt in explicitly in `.env`:

```env
FINDBREW_USE_MOCK_DATA=true
```

These development-only records use a neutral fallback illustration unless a verified provider photo is available. Set the value to `false` for normal use.

## Privacy and Persistence

Searches are sent to the configured Google provider. Favorites and preferences are stored in the current Streamlit session and are not persisted to an account or database.
