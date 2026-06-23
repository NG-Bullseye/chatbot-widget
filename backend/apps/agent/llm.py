import os

from langchain_openai import ChatOpenAI


def get_llm(streaming: bool = True) -> ChatOpenAI:
    """Provider-agnostic chat model.

    Default is DeepSeek V3 via its OpenAI-compatible endpoint. Point
    LLM_BASE_URL / LLM_MODEL / LLM_API_KEY at any OpenAI-compatible provider
    (Groq, Together, OpenRouter, OpenAI, ...) to swap without code changes.
    """
    return ChatOpenAI(
        model=os.environ.get("LLM_MODEL", "deepseek-chat"),
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=float(os.environ.get("LLM_TEMPERATURE", "0.3")),
        streaming=streaming,
    )
