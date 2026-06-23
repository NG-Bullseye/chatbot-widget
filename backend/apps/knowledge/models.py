from django.db import models
from pgvector.django import VectorField

from .embeddings import EMBEDDING_DIM


class Document(models.Model):
    """A source document (FAQ page, manual section, ...) editable via admin."""

    title = models.CharField(max_length=255)
    source = models.CharField(max_length=512, blank=True, help_text="URL or file path")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Chunk(models.Model):
    """A chunk of a Document with its embedding for similarity search."""

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.document.title} #{self.pk}"
