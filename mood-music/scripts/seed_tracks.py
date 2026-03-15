import requests
import base64
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

def get_token():
    credentials = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {credentials}"},
        data={"grant_type": "client_credentials"}
    )
    res.raise_for_status()
    return res.json()["access_token"]


# ─────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────

def search_tracks(query, token, limit=50):
    res = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "track", "limit": limit}
    )
    res.raise_for_status()
    items = res.json()["tracks"]["items"]

    return [
        {
            "spotify_id": t["id"],
            "title":      t["name"],
            "artist":     t["artists"][0]["name"],
            "popularity": t["popularity"]
        }
        for t in items
    ]


# ─────────────────────────────────────────
# AUDIO FEATURES
# ─────────────────────────────────────────

def get_audio_features(spotify_ids, token):
    chunks = [spotify_ids[i:i+100] for i in range(0, len(spotify_ids), 100)]
    all_features = []

    for chunk in chunks:
        res = requests.get(
            "https://api.spotify.com/v1/audio-features",
            headers={"Authorization": f"Bearer {token}"},
            params={"ids": ",".join(chunk)}
        )
        res.raise_for_status()
        all_features.extend(res.json()["audio_features"])
        time.sleep(0.1)

    return all_features


# ─────────────────────────────────────────
# MERGE
# ─────────────────────────────────────────

def enrich_tracks(tracks, features):
    feature_map = {f["id"]: f for f in features if f is not None}
    enriched = []

    for track in tracks:
        feat = feature_map.get(track["spotify_id"])
        if not feat:
            continue

        enriched.append({
            "spotify_id":        track["spotify_id"],
            "title":             track["title"],
            "artist":            track["artist"],
            "popularity":        track["popularity"],
            "valence":           feat["valence"],
            "arousal":           feat["energy"],
            "tempo":             feat["tempo"],
            "mode":              feat["mode"],
            "acousticness":      feat["acousticness"],
            "instrumentalness":  feat["instrumentalness"],
            "speechiness":       feat["speechiness"],
            "loudness":          feat["loudness"],
        })

    return enriched


# ─────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────

def filter_tracks(tracks):
    return [
        t for t in tracks
        if t["speechiness"]       < 0.1
        and t["instrumentalness"] > 0.3
        and t["popularity"]       > 10
    ]


# ─────────────────────────────────────────
# MOOD QUERIES
# ─────────────────────────────────────────

MOOD_QUERIES = {
    "grief":   [
        "sad piano rain",
        "melancholy strings orchestral",
        "lonely acoustic guitar",
    ],
    "anxious": [
        "tense ambient instrumental",
        "dark strings calm",
        "anxiety relief music",
    ],
    "tired":   [
        "slow ambient night",
        "soft instrumental sleep",
        "drone calm meditation",
    ],
    "calm":    [
        "peaceful ambient nature",
        "meditation piano instrumental",
        "calm focus instrumental",
    ],
    "hopeful": [
        "gentle uplifting acoustic",
        "morning piano instrumental",
        "positive ambient",
    ],
}


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("Getting Spotify token...")
    token = get_token()

    all_results = []
    seen_ids    = set()

    for mood, queries in MOOD_QUERIES.items():
        print(f"\n── Mood: {mood.upper()} ──")

        for query in queries:
            print(f"  Searching: '{query}'")

            tracks   = search_tracks(query, token, limit=50)
            ids      = [t["spotify_id"] for t in tracks]
            features = get_audio_features(ids, token)
            enriched = enrich_tracks(tracks, features)
            filtered = filter_tracks(enriched)

            new_tracks = []
            for t in filtered:
                if t["spotify_id"] not in seen_ids:
                    seen_ids.add(t["spotify_id"])
                    t["mood"] = mood
                    new_tracks.append(t)

            all_results.extend(new_tracks)
            print(f"  -> {len(new_tracks)} tracks added")

            time.sleep(0.5)

    output_path = os.path.join(os.path.dirname(__file__), "../data/tracks.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nDone. Total unique tracks: {len(all_results)}")
    print(f"Saved to data/tracks.json")

if __name__ == "__main__":
    main()
