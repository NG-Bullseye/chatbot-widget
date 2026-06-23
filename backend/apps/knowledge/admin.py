from django.contrib import admin, messages

from .ingest import ingest_document
from .models import Chunk, Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "updated_at")
    search_fields = ("title", "content")
    actions = ("reindex",)

    @admin.action(description="Reindex selected documents (rebuild embeddings)")
    def reindex(self, request, queryset):
        total = sum(ingest_document(doc) for doc in queryset)
        messages.success(request, f"{total} chunks neu erzeugt.")


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "created_at")
    search_fields = ("content",)
