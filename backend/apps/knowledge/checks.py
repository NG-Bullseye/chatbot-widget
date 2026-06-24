from django.core.checks import Error, register

from .embeddings import EMBEDDING_DIM


@register("knowledge")
def embedding_dim_matches_db(app_configs, **kwargs):
    """Fail fast when EMBEDDING_DIM no longer matches the vector column in the
    DB.

    The chunk embedding column's dimension is frozen into the migration at
    makemigrations time. If EMBEDDING_DIM (and thus EMBEDDING_MODEL) is changed
    afterwards, the env and the existing column silently disagree until the next
    insert blows up deep inside pgvector with an opaque DataError. This check
    surfaces the mismatch at startup with an actionable message instead.
    """
    from django.db import connection

    try:
        with connection.cursor() as cur:
            # pgvector stores the declared dimension in atttypmod.
            cur.execute(
                """
                SELECT a.atttypmod
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                WHERE c.relname = 'knowledge_chunk' AND a.attname = 'embedding'
                """
            )
            row = cur.fetchone()
    except Exception:
        # DB not migrated / not reachable (e.g. plain `manage.py check`,
        # collectstatic, build step). Nothing to validate yet.
        return []

    if not row or row[0] in (None, -1):
        return []

    db_dim = row[0]
    if db_dim != EMBEDDING_DIM:
        return [
            Error(
                f"EMBEDDING_DIM={EMBEDDING_DIM} but knowledge_chunk.embedding is "
                f"vector({db_dim}) in the database.",
                hint=(
                    "Changing the embedding model/dimension requires a migration "
                    "and a full re-index. Run `makemigrations knowledge` + "
                    "`migrate`, then re-index all Documents (admin action "
                    "'Reindex'). Old embeddings are not convertible."
                ),
                id="knowledge.E001",
            )
        ]
    return []
