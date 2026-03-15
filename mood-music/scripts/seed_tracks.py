import requests
import base64
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


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


def search_tracks(query, token, limit=10):
    res = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "track", "limit": limit}
    )
    res.raise_for_status()
    items = res.json()["tracks"]["items"]
    return [
        {
            "spotify_id":  t["id"],
            "title":       t["name"],
            "artist":      t["artists"][0]["name"],
            "explicit":    t.get("explicit", False),
            "duration_ms": t.get("duration_ms", 0),
        }
        for t in items
    ]


# Mood queries with manually assigned coordinates
# valence: 0=sad -> 1=happy
# arousal: 0=calm -> 1=energetic
MOOD_QUERIES = {
    "grief": {
        "valence": 0.10, "arousal": 0.15,
        "queries": [
            "sad piano instrumental",
            "melancholy classical strings",
            "grief ambient music",
            "lonely acoustic instrumental",
        ]
    },
    "anxious": {
        "valence": 0.20, "arousal": 0.70,
        "queries": [
            "anxious tense instrumental",
            "stress relief calm music",
            "anxiety ambient instrumental",
        ]
    },
    "tired": {
        "valence": 0.35, "arousal": 0.15,
        "queries": [
            "sleep music instrumental",
            "slow ambient night music",
            "exhausted calm piano",
        ]
    },
    "calm": {
        "valence": 0.65, "arousal": 0.20,
        "queries": [
            "peaceful piano instrumental",
            "meditation calm ambient",
            "nature sounds relaxing music",
            "lofi calm focus",
        ]
    },
    "hopeful": {
        "valence": 0.75, "arousal": 0.45,
        "queries": [
            "uplifting acoustic instrumental",
            "hopeful morning piano",
            "gentle positive ambient",
        ]
    },
}


def main():
    print("Getting Spotify token...")
    token = get_token()

    all_results = []
    seen_ids    = set()

    for mood, config in MOOD_QUERIES.items():
        print(f"\n-- Mood: {mood.upper()} "
              f"(valence={config['valence']}, arousal={config['arousal']}) --")

        for query in config["queries"]:
            print(f"  Searching: '{query}'")

            try:
                tracks = search_tracks(query, token, limit=10)
            except Exception as e:
                print(f"  Error: {e}")
                continue

            new_tracks = []
            for t in tracks:
                if t["spotify_id"] in seen_ids:
                    continue
                if t["explicit"]:
                    continue

                seen_ids.add(t["spotify_id"])
                new_tracks.append({
                    "spotify_id":  t["spotify_id"],
                    "title":       t["title"],
                    "artist":      t["artist"],
                    "duration_ms": t["duration_ms"],
                    "mood":        mood,
                    "valence":     config["valence"],
                    "arousal":     config["arousal"],
                    "tempo_norm":  config["arousal"],
                })

            all_results.extend(new_tracks)
            print(f"  -> {len(new_tracks)} tracks added")
            time.sleep(0.3)

    os.makedirs(os.path.join(os.path.dirname(__file__), "../data"), exist_ok=True)
    output_path = os.path.join(os.path.dirname(__file__), "../data/tracks.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Total unique tracks: {len(all_results)}")
    print("Saved to data/tracks.json")


if __name__ == "__main__":
    main()
