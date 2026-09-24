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
_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)
_LEFT_REFERENTIAL = {
    "about", "with", "from", "to", "for", "where", "saw", "see", "seen",
    "heard", "ask", "asked", "find", "found", "contact", "trust", "trusted",
    "miss", "missed", "remember", "remembered",
}
_RIGHT_REFERENTIAL = {
    "is", "was", "has", "had", "said", "says", "told", "promised",
    "expects", "expected", "returned", "returns", "left", "came", "comes",
    "seems", "seemed", "might", "could", "would", "should", "did", "does",
}


def _ordered_words(text: str) -> list[str]:
    return [match.group(0).casefold() for match in _WORD_RE.finditer(text)]


def _actor_is_referential(text: str, actor: str) -> bool:
    """Recognize a bounded actor span without treating ordinary verbs as names.

    Single-token actors require local referential context. This intentionally
    sacrifices some ellipsis and bare-name recall so names such as Will, Hope,
    May, Mark or Bill do not gain support from ordinary word usage.
    """
    actor_words = _ordered_words(actor)
    words = _ordered_words(text)
    if not actor_words or not words:
        return False
    if len(actor_words) > 1:
        width = len(actor_words)
        return any(words[index:index + width] == actor_words
                   for index in range(len(words) - width + 1))
    target = actor_words[0]
    if len(words) == 1:
        return words[0] == target
    for index, word in enumerate(words):
        if word != target:
            continue
        left = words[index - 1] if index else ""
        right = words[index + 1] if index + 1 < len(words) else ""
        if left in _LEFT_REFERENTIAL or right in _RIGHT_REFERENTIAL:
            return True
    return False


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
    actors = tuple(sorted(actor for actor in anchors if _actor_is_referential(text, actor)))
    # Fail closed on elliptical omitted subjects. With exactly one visible actor,
    # only an explicit personal pronoun can inherit that discourse referent.
    # "I should check the stove" must not become evidence about Mara merely
    # because Mara is the only actor currently grounded in the workspace.
    if not actors and len(anchors) == 1 and words & _PRONOUNS:
        actors = tuple(anchors)
    support = tuple(dict.fromkeys(link for actor in actors for link in anchors[actor]))
    return ThoughtMeaning(actors, operation, modality, support)
