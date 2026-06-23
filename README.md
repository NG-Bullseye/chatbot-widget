# chatbot-widget

Customer-agnostic website chatbot. Django + LangGraph + Langfuse, embeddable on
any site via a single `<script>` tag. Answers customer questions with a cheap,
swappable LLM endpoint (DeepSeek V3 by default) and RAG over a pgvector
knowledge base.

Everything customer-specific lives in `.env` / `config/customer.*.yaml`. No
customer data in the code.

## Architecture

```
website  --script tag-->  widget (Shadow DOM, slide-out panel)
                              |  POST /api/chat (SSE stream)
                              v
Django (async view)  -->  LangGraph: retrieve (pgvector) -> generate (LLM)
                              |                                   |
                          Postgres + pgvector              DeepSeek V3
                              |
                          Langfuse (self-hosted)  <-- traces + feedback scores
```

- **backend/** Django project. `apps/chat` (API + conversation logs),
  `apps/agent` (LangGraph, DB-free), `apps/knowledge` (pgvector RAG).
- **widget/** embeddable frontend, vanilla JS, Shadow DOM.
- **config/** per-customer config reference.

The graph stays free of sync ORM writes: the view loads history and persists
the turn around the stream; only read-only async pgvector retrieval runs inside
the graph.

## Local setup

```bash
# 1. Infra (Postgres+pgvector, Langfuse)
docker compose up -d db langfuse langfuse-db

# 2. Backend
cd backend
cp .env.example .env          # fill in LLM_API_KEY, EMBEDDING_API_KEY, LANGFUSE_*
pip install -e .
python manage.py migrate knowledge 0001_pgvector   # enable pgvector first
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
uvicorn config.asgi:application --reload
```

Get Langfuse keys from http://localhost:3000 (create project), put them in `.env`.

Add knowledge: Django admin (`/admin`) -> Documents -> add -> select -> action
"Reindex" to build embeddings.

## Embed on a site

```html
<script src="https://YOUR-HOST/embed.js"
        data-bot-api="https://YOUR-HOST/api"
        data-position="right"
        data-accent="#e87722"
        data-title="Support"
        data-greeting="Hallo! Wie kann ich helfen?" defer></script>
```

## Swap the LLM

Point `LLM_BASE_URL` / `LLM_MODEL` / `LLM_API_KEY` at any OpenAI-compatible
provider (DeepSeek, Groq, Together, OpenRouter, OpenAI). No code change.
