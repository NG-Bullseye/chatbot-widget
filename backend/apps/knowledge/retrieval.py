from asgiref.sync import sync_to_async
from pgvector.django import L2Distance

from .embeddings import get_embeddings
from .models import Chunk


@sync_to_async
def _query(vector, k: int):
    # Materialize inside the sync context so the ORM query actually runs here.
    return list(
        Chunk.objects.order_by(L2Distance("embedding", vector))[:k]
    )


async def similar_chunks(text: str, k: int = 4):
    """Embed the query text and return the k nearest chunks via pgvector.

    Embedding is a network call (async); the ORM query is wrapped in
    sync_to_async so it is safe to call from the async graph.
    """
    vector = await get_embeddings().aembed_query(text)
    return await _query(vector, k)
