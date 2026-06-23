"""Ingestion: turn a Document's text into embedded chunks.

Usage (management shell or a custom command):
    from apps.knowledge.ingest import ingest_document
    ingest_document(doc)
"""
from .embeddings import get_embeddings
from .models import Chunk, Document


def _split(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Naive character splitter with overlap. Swap for a smarter splitter
    (e.g. langchain RecursiveCharacterTextSplitter) when needed."""
    chunks, start = [], 0
    text = text.strip()
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return [c for c in chunks if c.strip()]


def ingest_document(document: Document) -> int:
    """(Re)build chunks for a document. Returns number of chunks created."""
    document.chunks.all().delete()
    pieces = _split(document.content)
    if not pieces:
        return 0
    vectors = get_embeddings().embed_documents(pieces)
    Chunk.objects.bulk_create(
        [
            Chunk(document=document, content=piece, embedding=vector)
            for piece, vector in zip(pieces, vectors)
        ]
    )
    return len(pieces)
