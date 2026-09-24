"""Adaptations inside the Persona-and-Jelly engine's existing decision authority."""
from digital_subject.engine import SubjectEngine, clamp
from digital_subject.models import Event


class Organism(SubjectEngine):
    def advance_body(self):
        self._advance_time(1)

    def recall(self, concepts):
        return self._retrieve_memories(concepts, self.top_k)

    def appraise_recollection(self, memory):
        """A remembered event may change present affect, never its objective status.

        This reuses the donor's memory valence rule and existing pressure channels.
        The caller enforces per-evidence cooldown, so paraphrases cannot amplify
        the same support repeatedly inside one heartbeat.
        """
        valence = self._memory_valence(memory)
        delta = min(0.08, abs(valence) * 0.08)
        key = "fear" if valence < 0 else "trust" if valence > 0 else "arousal"
        delta = delta if valence else 0.015
        before = self.state.pressures.get(key, 0.0)
        self._adjust_pressure(key, delta)
        memory.last_recalled_tick = self.state.tick
        memory.recall_count += 1
        memory.strength = clamp(memory.strength + 0.025)
        return key, self.state.pressures[key] - before

    def select_conduct(self, event: Event | None = None):
        """The same selector handles external input and private cognitive aftermath."""
        intention = self._choose_intention(
            event or Event("temporal", "self", "Time passes."),
            self._triage_needs(), self._triage_pressures())
        self.state.last_intention = intention
        self.state.current_activity = intention
        return intention

    def finish_silent_activity(self, action):
        # Donor activities are internal regulation, not claims of external success.
        activity = next((a for a in self.cartridge.activities if a.action == action), None)
        if activity is None:
            experience = self._record_experience("intention", "I consider what to do next.", 0.2, (action.value,))
        else:
            experience = self._perform_activity(activity)
        self._maybe_reflect()
        return experience
