import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _enabled() -> bool:
    return bool(os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"))


def start_trace(session_id: str, user_input: str) -> tuple[str | None, list]:
    """Open a Langfuse trace for one chat turn.

    Returns (trace_id, callbacks). The LangChain handler is bound to an
    explicit trace so its id can be returned to the widget and later used to
    attach the user's feedback to exactly this turn (see score_feedback).
    Returns (None, []) when Langfuse isn't configured, so the app runs without
    observability wired up.
    """
    if not _enabled():
        return None, []
    from langfuse import Langfuse

    trace = Langfuse().trace(name="chat", session_id=session_id, input=user_input)
    return trace.id, [trace.get_langchain_handler()]


def score_feedback(trace_id: str, value: int, comment: str = "") -> None:
    """Attach a thumbs up/down (value 1 or -1) to a chat trace."""
    if not _enabled():
        return
    from langfuse import Langfuse

    Langfuse().score(trace_id=trace_id, name="user_feedback", value=value, comment=comment)
