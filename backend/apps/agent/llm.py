import os

from langchain_openai import ChatOpenAI


def get_llm(streaming: bool = True) -> ChatOpenAI:
    """Provider-agnostic chat model.

    Point LLM_BASE_URL / LLM_MODEL / LLM_API_KEY at any OpenAI-compatible
    provider (Mistral, Groq, Together, OpenRouter, OpenAI, ...) to swap
    without code changes.

    No defaults for base URL and model on purpose: chat input is free text and
    potentially personal data, so the destination of that data must be an
    explicit deployment decision. A missing env var has to fail the boot, not
    silently route traffic to whatever the code happened to ship with.
    """
    return ChatOpenAI(
        model=os.environ["LLM_MODEL"],
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
        temperature=float(os.environ.get("LLM_TEMPERATURE", "0.3")),
        streaming=streaming,
    )
