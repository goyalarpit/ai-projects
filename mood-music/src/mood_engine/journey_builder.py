"""
Computes 3-phase mood journey targets.

Phase 1: Meet the user where they are  (current mood)
Phase 2: Gentle bridge                 (midpoint toward calm)
Phase 3: Calm landing zone             (destination)

Calm target is fixed: valence=0.65, arousal=0.20
"""

CALM_TARGET = {"valence": 0.65, "arousal": 0.20}


def build_journey(current_valence, current_arousal):
    """
    Given current mood coordinates, return 3 phase targets.

    Returns:
    {
        "phase1": { "valence": ..., "arousal": ... },
        "phase2": { "valence": ..., "arousal": ... },
        "phase3": { "valence": ..., "arousal": ... },
    }
    """
    cv = current_valence
    ca = current_arousal
    tv = CALM_TARGET["valence"]
    ta = CALM_TARGET["arousal"]

    return {
        "phase1": {
            "valence": round(cv, 3),
            "arousal": round(ca, 3),
        },
        "phase2": {
            "valence": round((cv + tv) / 2, 3),
            "arousal": round((ca + ta) / 2, 3),
        },
        "phase3": {
            "valence": round(tv, 3),
            "arousal": round(ta, 3),
        },
    }


def phase_labels(primary_emotion):
    """Human-readable labels for each phase based on user's emotion."""
    labels = {
        "grief":     ["Sitting with how you feel", "Gently lifting", "Arriving at peace"],
        "anxious":   ["Acknowledging the tension", "Slowing down", "Settling into calm"],
        "exhausted": ["Honouring your tiredness", "Softening", "Restoring"],
        "tired":     ["Honouring your tiredness", "Softening", "Restoring"],
        "angry":     ["Letting it be felt", "Finding space", "Coming to stillness"],
        "sad":       ["Being with the sadness", "A gentle shift", "Quiet warmth"],
        "overwhelmed":["Making space", "Breathing out", "Finding ground"],
    }
    default = ["Where you are now", "Finding your way", "Arriving at calm"]
    return labels.get(primary_emotion.lower(), default)


# ─────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────
if __name__ == "__main__":
    # Simulate an exhausted user
    journey = build_journey(current_valence=0.20, current_arousal=0.35)
    labels  = phase_labels("exhausted")

    print("Journey phases:")
    for i, (phase, coords) in enumerate(journey.items()):
        print(f"  {phase} | {labels[i]:30} | valence={coords['valence']}  arousal={coords['arousal']}")
