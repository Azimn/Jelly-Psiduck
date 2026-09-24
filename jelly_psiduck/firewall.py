"""Phenomenological projection; raw numbers never become cognition arguments."""
from digital_subject.models import Memory


NEED_LANGUAGE = {
    "hunger": "I'm hungry.", "thirst": "I'm thirsty.", "fatigue": "I'm tired.",
    "energy": "I feel drained.", "warmth": "I'm getting cold.",
    "comfort": "I'm uncomfortable.", "pain": "I'm hurting.",
    "loneliness": "I miss having company.", "safety": "I don't feel safe.",
    "focus": "I'm finding it hard to concentrate.",
    "restlessness": "I feel restless.", "curiosity": "I want to explore.",
    "satisfaction": "Something feels unfulfilled.",
}
LOW_IS_BAD = frozenset({"energy", "warmth", "comfort", "safety", "focus", "satisfaction"})


def body_experiences(state):
    for key, text in NEED_LANGUAGE.items():
        value = state.needs.get(key, 0.5)
        urgency = 1 - value if key in LOW_IS_BAD else value
        if urgency >= 0.6:
            yield key, text, urgency


def remembered(memory: Memory) -> str:
    # Strength is a retrieval-quality heuristic, not a calibrated truth probability.
    if memory.strength < 0.2:
        return "Something about this feels familiar, but I cannot recover the details."
    if memory.strength < 0.5:
        return f"I vaguely remember this event: {memory.summary} {memory.meaning}"
    return f"I remember this event: {memory.summary} {memory.meaning}"
