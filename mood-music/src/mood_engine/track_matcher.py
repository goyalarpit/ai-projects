import json
import math
import os

TRACKS_PATH = os.path.join(os.path.dirname(__file__), "../../data/tracks.json")


def load_tracks():
    with open(TRACKS_PATH, encoding="utf-8") as f:
        return json.load(f)


def distance(v1, a1, v2, a2):
    """Euclidean distance between two mood coordinates."""
    return math.sqrt((v1 - v2) ** 2 + (a1 - a2) ** 2)


def find_tracks_for_phase(target_valence, target_arousal, tracks, exclude_ids=None, n=5):
    """
    Find n tracks closest to target mood coordinates.
    Excludes track IDs already used in previous phases.
    """
    if exclude_ids is None:
        exclude_ids = set()

    scored = []
    for track in tracks:
        if track["spotify_id"] in exclude_ids:
            continue

        dist = distance(
            target_valence, target_arousal,
            track["valence"],  track["arousal"]
        )
        scored.append((dist, track))

    scored.sort(key=lambda x: x[0])
    return [t for _, t in scored[:n]]


def match_playlist(phase_targets, n_per_phase=5):
    """
    Given 3 phase targets, return matched tracks for each phase.

    phase_targets = {
        "phase1": { "valence": 0.20, "arousal": 0.35 },
        "phase2": { "valence": 0.43, "arousal": 0.28 },
        "phase3": { "valence": 0.65, "arousal": 0.20 },
    }
    """
    tracks     = load_tracks()
    used_ids   = set()
    playlist   = {}

    for phase, coords in phase_targets.items():
        matched = find_tracks_for_phase(
            target_valence=coords["valence"],
            target_arousal=coords["arousal"],
            tracks=tracks,
            exclude_ids=used_ids,
            n=n_per_phase
        )
        playlist[phase] = matched
        used_ids.update(t["spotify_id"] for t in matched)

    return playlist


# ─────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────
if __name__ == "__main__":
    phase_targets = {
        "phase1": {"valence": 0.20, "arousal": 0.35},
        "phase2": {"valence": 0.43, "arousal": 0.28},
        "phase3": {"valence": 0.65, "arousal": 0.20},
    }

    playlist = match_playlist(phase_targets)

    for phase, tracks in playlist.items():
        print(f"\n{phase.upper()}:")
        for t in tracks:
            print(f"  [{t['mood']:8}] v={t['valence']} a={t['arousal']} "
                  f"| {t['title']} - {t['artist']}")
