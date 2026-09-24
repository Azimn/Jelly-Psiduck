"""A bounded discourse interpreter, not a general semantic judge.

Names must be grounded in visible experience. Pronouns and omitted subjects are
resolved only with one eligible discourse referent. Modality and cognitive intent
remain engine-side annotations and never grant truth or action authority.
"""
import re
from dataclasses import dataclass

from .runtime import concepts


_PRONOUNS = {"she", "he", "they", "her", "him", "them"}
_NEGATION_RE = re.compile(
    r"\b(?:not|never|no|cannot)\b|\b\w+n['’]t\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ThoughtMeaning:
    actors: tuple[str, ...]
    operation: str
    modality: str
    support: tuple[str, ...]


def interpret(text: str, anchors: dict[str, tuple[str, ...]]) -> ThoughtMeaning:
    words = concepts(text)
    operation = "recall"
    if words & {"check", "look", "ask", "find", "seek"}:
        operation = "inquire"
    elif words & {"back", "return", "late", "waiting", "wait", "promised", "expect", "expected", "where", "delayed"}:
        operation = "anticipate"
    elif words & {"worry", "worried", "afraid", "danger", "happened", "safe"}:
        operation = "concern"
    modality = "uncertain" if "?" in text or words & {"maybe", "might", "perhaps", "wonder", "could"} else "asserted"
    if _NEGATION_RE.search(text):
        modality = "negated_or_uncertain"
    actors = tuple(sorted(actor for actor in anchors if concepts(actor) <= words))
    # Fail closed on elliptical omitted subjects. With exactly one visible actor,
    # only an explicit personal pronoun can inherit that discourse referent.
    # "I should check the stove" must not become evidence about Mara merely
    # because Mara is the only actor currently grounded in the workspace.
    if not actors and len(anchors) == 1 and words & _PRONOUNS:
        actors = tuple(anchors)
    support = tuple(dict.fromkeys(link for actor in actors for link in anchors[actor]))
    return ThoughtMeaning(actors, operation, modality, support)
