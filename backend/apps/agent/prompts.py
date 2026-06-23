import os
from pathlib import Path

DEFAULT_SYSTEM_PROMPT = (
    "Du bist ein freundlicher Support-Assistent auf einer Unternehmenswebsite. "
    "Beantworte Kundenfragen kurz, praezise und hilfsbereit. "
    "Nutze ausschliesslich die Informationen aus dem bereitgestellten Kontext. "
    "Wenn der Kontext die Antwort nicht enthaelt, sage ehrlich, dass du es nicht "
    "weisst und biete an, an einen Menschen weiterzuleiten. Erfinde nichts."
)


def load_system_prompt() -> str:
    """System prompt is customer-specific. Load from SYSTEM_PROMPT_FILE if set,
    else from the SYSTEM_PROMPT env var, else fall back to the default."""
    path = os.environ.get("SYSTEM_PROMPT_FILE")
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8").strip()
    return os.environ.get("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)


def build_system_prompt(context: str) -> str:
    base = load_system_prompt()
    if context:
        return f"{base}\n\n--- Wissensbasis-Kontext ---\n{context}"
    return base
