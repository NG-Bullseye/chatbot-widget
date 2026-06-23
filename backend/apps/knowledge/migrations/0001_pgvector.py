from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    """Enable the pgvector extension before any VectorField tables are created.
    Run `python manage.py makemigrations knowledge` afterwards to generate the
    model tables (they will depend on this migration)."""

    initial = True
    dependencies = []
    operations = [VectorExtension()]
