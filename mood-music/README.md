# Mood Music

A voice-first platform that listens to how you feel and guides you back to calm through a personalized musical journey.

## Structure

```
mood-music/
├── data/               # Track database (JSON / PostgreSQL)
├── scripts/            # One-time data seeding scripts
│   └── seed_tracks.py  # Fetch tracks from Spotify API
├── src/
│   ├── voice/          # Voice capture & transcription
│   ├── mood_engine/    # Mood profiling & track matching
│   └── api/            # Backend API
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your keys to .env
```

## Seed Track Database

```bash
python scripts/seed_tracks.py
```
