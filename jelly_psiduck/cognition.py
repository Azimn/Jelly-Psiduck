"""Optional private-language providers. Neither provider gets organism telemetry."""
import json
import urllib.request
from dataclasses import asdict
from typing import Protocol

from .workspace import CognitiveView, Thought


COGNITIVE_PROMPT_VERSION = "private-thought-json-v1"
DEFAULT_MAX_TOKENS = 220
DEFAULT_TEMPERATURE = 0.4


class Cognition(Protocol):
    def think(self, view: CognitiveView) -> Thought | None: ...


class ReflectiveCognition:
    """Deterministic control, intentionally limited; no claim of free-form reasoning."""
    def think(self, view: CognitiveView) -> Thought | None:
        for experience in reversed(view.experiences):
            if experience.source in {"memory", "temporal"}:
                return Thought(f"I keep considering this: {experience.first_person}")
            if experience.source == "interoception":
                return Thought(f"I should attend to how I feel. {experience.first_person}")
        return None


def cognitive_prompt(view: CognitiveView) -> str:
    return (
        "These are my experiences. Memories can be uncertain; thoughts and imagination "
        "are not observations. Consider one private thought or remain silent. "
        "Return only JSON with a single field text (string or null). "
        "Do not issue actions or speak to anyone.\n"
        + json.dumps(asdict(view), ensure_ascii=False)
    )


class OpenAICompatibleCognition:
    """Explicitly configured chat-completions transport, no mandatory model service."""
    def __init__(self, endpoint: str, model: str, api_key: str = "", timeout: float = 30):
        self.endpoint = endpoint.rstrip("/") + "/chat/completions"
        self.model, self.api_key, self.timeout = model, api_key, timeout

    def think(self, view: CognitiveView) -> Thought | None:
        data = json.dumps({"model": self.model, "messages": [
            {"role": "user", "content": cognitive_prompt(view)}],
            "max_tokens": DEFAULT_MAX_TOKENS, "temperature": DEFAULT_TEMPERATURE}).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.endpoint, data=data, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = response.read(65537)
        if len(payload) > 65536:
            raise ValueError("model response too large")
        result = json.loads(payload)
        parsed = json.loads(result["choices"][0]["message"]["content"])
        if not isinstance(parsed, dict) or set(parsed) != {"text"}:
            raise ValueError("expected only text")
        text = parsed["text"]
        if text is None:
            return None
        if not isinstance(text, str) or not 0 < len(text.strip()) <= 600:
            raise ValueError("invalid thought text")
        return Thought(text.strip())
