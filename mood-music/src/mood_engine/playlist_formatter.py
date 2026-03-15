"""
Combines all mood engine layers into a final playlist response.

Input:  user transcript (from voice)
Output: 3-phase playlist with Spotify deep links
"""

import json
import uuid
from datetime import datetime

from mood_profiler  import profile_mood
from journey_builder import build_journey, phase_labels
from track_matcher  import match_playlist


def spotify_links(spotify_id):
    return {
        "web": f"https://open.spotify.com/track/{spotify_id}",
        "app": f"spotify:track:{spotify_id}",
    }


def format_duration(ms):
    secs  = ms // 1000
    mins  = secs // 60
    secs  = secs % 60
    return f"{mins}:{secs:02d}"


def build_response(transcript: str) -> dict:
    """
    Full pipeline: transcript -> mood profile -> journey -> playlist.
    """

    # Layer 2: Mood profile
    print("  Analyzing mood...")
    profile = profile_mood(transcript)

    # Layer 3: Journey targets
    journey_targets = build_journey(
        current_valence=profile["valence"],
        current_arousal=profile["arousal"],
    )
    labels = phase_labels(profile["primary_emotion"])

    # Layer 4: Track matching
    print("  Matching tracks...")
    matched = match_playlist(journey_targets, n_per_phase=5)

    # Layer 5: Format response
    phases = []
    for i, (phase, tracks) in enumerate(matched.items()):
        phases.append({
            "phase":       i + 1,
            "label":       labels[i],
            "coordinates": journey_targets[phase],
            "tracks": [
                {
                    "title":       t["title"],
                    "artist":      t["artist"],
                    "duration":    format_duration(t.get("duration_ms", 0)),
                    "mood_tag":    t["mood"],
                    "spotify":     spotify_links(t["spotify_id"]),
                }
                for t in tracks
            ]
        })

    return {
        "session_id":    str(uuid.uuid4()),
        "timestamp":     datetime.utcnow().isoformat() + "Z",
        "user_mood": {
            "primary_emotion": profile["primary_emotion"],
            "themes":          profile.get("themes", []),
            "intensity":       profile.get("intensity", 0.5),
            "summary":         profile.get("summary", ""),
            "coordinates": {
                "valence": profile["valence"],
                "arousal": profile["arousal"],
            }
        },
        "journey": phases,
    }


# ─────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────
if __name__ == "__main__":
    transcript = (
        "I've just had such a long day. Work was really stressful, "
        "I couldn't focus on anything and my mind keeps racing. "
        "I feel tense and I just can't seem to switch off."
    )

    print("Running full mood engine pipeline...")
    print()

    result = build_response(transcript)

    print()
    print(f"Session: {result['session_id']}")
    print(f"Detected mood: {result['user_mood']['primary_emotion']} "
          f"(intensity: {result['user_mood']['intensity']})")
    print(f"Summary: {result['user_mood']['summary']}")
    print()

    for phase in result["journey"]:
        print(f"Phase {phase['phase']}: {phase['label']}")
        for t in phase["tracks"]:
            print(f"  - {t['title']} by {t['artist']} ({t['duration']})")
            print(f"    {t['spotify']['web']}")
        print()

    # Also save full JSON
    with open("data/sample_response.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("Full response saved to data/sample_response.json")
