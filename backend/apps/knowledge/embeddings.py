import os

from langchain_openai import OpenAIEmbeddings

# Keep this in sync with the dimensions of EMBEDDING_MODEL and with
# Chunk.embedding's VectorField dimensions (default: OpenAI
# text-embedding-3-small = 1536).
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", "1536"))


def get_embeddings() -> OpenAIEmbeddings:
    """Embeddings are configured separately from the chat LLM because most
    cheap chat providers (e.g. DeepSeek) do not serve embeddings. Defaults to
    OpenAI; override EMBEDDING_BASE_URL / EMBEDDING_MODEL / EMBEDDING_API_KEY
    for any OpenAI-compatible embedding endpoint."""
    return OpenAIEmbeddings(
        model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
        api_key=os.environ.get("EMBEDDING_API_KEY", os.environ.get("LLM_API_KEY")),
        base_url=os.environ.get("EMBEDDING_BASE_URL", "https://api.openai.com/v1"),
    )
