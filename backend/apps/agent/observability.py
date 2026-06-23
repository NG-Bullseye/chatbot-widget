import os
from functools import lru_cache


@lru_cache(maxsize=1)
def _enabled() -> bool:
    return bool(os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"))


def get_callbacks(session_id: str | None = None) -> list:
    """Return a Langfuse callback handler if configured, else an empty list so
    the app runs fine without observability wired up."""
    if not _enabled():
        return []
    from langfuse.callback import CallbackHandler

    handler = CallbackHandler(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
        session_id=session_id,
    )
    return [handler]
