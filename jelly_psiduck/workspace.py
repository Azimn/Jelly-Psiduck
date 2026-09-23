"""Engine-owned experience records and the smaller, immutable cognitive interface.

Records describe what was experienced, not whether their contents are true.
Only the runtime commits them. IDs, scores and support links are inspector data;
the replaceable cognition provider receives a detached CognitiveView instead.
"""
from dataclasses import asdict, dataclass


SOURCES = frozenset({"perception", "interoception", "memory", "thought",
                     "imagination", "social", "temporal", "action_consequence"})


@dataclass(frozen=True, slots=True)
class SubjectiveExperience:
    id: str
    tick: int
    source: str
    first_person: str
    salience: float = 0.5
    intensity: float = 0.5
    concepts: tuple[str, ...] = ()
    affect: tuple[str, ...] = ()
    memory_links: tuple[str, ...] = ()
    concern_links: tuple[str, ...] = ()
    expectation_links: tuple[str, ...] = ()
    generated_by: str | None = None
    private: bool = True
    available_to_cognition: bool = True


@dataclass(frozen=True, slots=True)
class FeltExperience:
    # Source awareness prevents a recollection or imagination masquerading as sight.
    source: str
    first_person: str


@dataclass(frozen=True, slots=True)
class CognitiveView:
    experiences: tuple[FeltExperience, ...]


@dataclass(frozen=True, slots=True)
class Thought:
    text: str


class SubjectiveWorkspace:
    def __init__(self, records=(), sequence: int = 0, limit: int = 64):
        self.records = list(records)
        self.sequence = sequence
        self.limit = limit

    def add(self, tick: int, source: str, text: str, **metadata) -> SubjectiveExperience:
        if source not in SOURCES or not text.strip():
            raise ValueError("invalid subjective experience")
        self.sequence += 1
        item = SubjectiveExperience(f"experience-{self.sequence}", tick, source, text, **metadata)
        self.records.append(item)
        self.records = self.records[-self.limit:]
        return item

    def view(self) -> CognitiveView:
        return CognitiveView(tuple(FeltExperience(r.source, r.first_person)
                                   for r in self.records[-16:] if r.available_to_cognition))

    def to_dict(self):
        return {"records": [asdict(r) for r in self.records], "sequence": self.sequence}

    @classmethod
    def from_dict(cls, data):
        records = []
        for item in data.get("records", []):
            item = dict(item)
            for key in ("concepts", "affect", "memory_links", "concern_links", "expectation_links"):
                item[key] = tuple(item.get(key, ()))
            records.append(SubjectiveExperience(**item))
        return cls(records, data.get("sequence", 0))
