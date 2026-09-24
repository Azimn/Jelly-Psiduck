"""Optional private-language providers. Neither provider gets organism telemetry."""
import hashlib
import json
import urllib.request
from dataclasses import asdict
from typing import Protocol

from .workspace import CognitiveView, Thought


COGNITIVE_PROMPT_VERSION = "private-thought-json-v1"
IDENTITY_COGNITIVE_PROMPT_VERSION = "private-thought-json-v1+identity-v1"
MODEL_RESPONSE_PARSER_VERSION = "single-text-json-v1"
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


def cognitive_prompt(view: CognitiveView, identity: dict | None = None) -> str:
    base = (
        "These are my experiences. Memories can be uncertain; thoughts and imagination "
        "are not observations. Consider one private thought or remain silent. "
        "Return only JSON with a single field text (string or null). "
        "Do not issue actions or speak to anyone.\n"
        + json.dumps(asdict(view), ensure_ascii=False)
    )
    if not identity:
        return base
    return (
        "This is enduring self-context, not a new event. Use it as identity orientation, "
        "but do not turn it into an observation or invent missing biography.\n"
        + json.dumps(identity, ensure_ascii=False, sort_keys=True)
        + "\n"
        + base
    )


def parse_text_json(content: str, *, max_chars: int) -> tuple[str | None, str]:
    """Parse the one-field contract with only a deterministic fence repair."""
    if not isinstance(content, str):
        raise ValueError("model message content must be text")
    stripped = content.strip()
    mode = "json"
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) < 3 or lines[-1].strip() != "```":
            raise ValueError("unterminated JSON fence")
        opener = lines[0].strip().casefold()
        if opener not in {"```", "```json"}:
            raise ValueError("unsupported code fence")
        stripped = "\n".join(lines[1:-1]).strip()
        mode = "fenced_json"
    elif "```" in stripped:
        raise ValueError("unexpected code fence")
    parsed = json.loads(stripped)
    if not isinstance(parsed, dict) or set(parsed) != {"text"}:
        raise ValueError("expected only text")
    text = parsed["text"]
    if text is None:
        return None, mode
    if not isinstance(text, str) or not 0 < len(text.strip()) <= max_chars:
        raise ValueError("invalid text field")
    return text.strip(), mode


class OpenAICompatibleCognition:
    """Explicitly configured chat-completions transport, no mandatory model service."""

    def __init__(
        self,
        endpoint: str,
        model: str,
        api_key: str = "",
        timeout: float = 30,
        identity: dict | None = None,
    ):
        self.endpoint = endpoint.rstrip("/") + "/chat/completions"
        self.model, self.api_key, self.timeout = model, api_key, timeout
        self.identity = dict(identity) if identity else None
        self.calls: list[dict] = []

    def prompt_for(self, view: CognitiveView) -> str:
        return cognitive_prompt(view, self.identity)

    def think(self, view: CognitiveView) -> Thought | None:
        prompt = self.prompt_for(view)
        call = {
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_contract": (IDENTITY_COGNITIVE_PROMPT_VERSION if self.identity else COGNITIVE_PROMPT_VERSION),
            "parser_version": MODEL_RESPONSE_PARSER_VERSION,
            "raw_content": None,
            "parse_mode": None,
            "output_text": None,
            "error_type": None,
        }
        try:
            data = json.dumps({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": DEFAULT_MAX_TOKENS,
                "temperature": DEFAULT_TEMPERATURE,
            }).encode()
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            request = urllib.request.Request(self.endpoint, data=data, headers=headers)
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read(65537)
            if len(payload) > 65536:
                raise ValueError("model response too large")
            result = json.loads(payload)
            content = result["choices"][0]["message"]["content"]
            call["raw_content"] = content
            text, mode = parse_text_json(content, max_chars=600)
            call["parse_mode"] = mode
            call["output_text"] = text
            self.calls.append(call)
            return None if text is None else Thought(text)
        except Exception as exc:
            call["error_type"] = type(exc).__name__
            self.calls.append(call)
            raise
