from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from .nodes.generate import generate
from .nodes.retrieve import retrieve
from .state import ChatState


@lru_cache(maxsize=1)
def get_graph():
    """Compile once and reuse. Flow:

        START -> retrieve (pgvector RAG) -> generate (LLM) -> END

    Conversation history is supplied per request by the caller (the Django
    view loads it from the DB), so the graph itself stays stateless / DB-free
    apart from the read-only retrieval query.
    """
    g = StateGraph(ChatState)
    g.add_node("retrieve", retrieve)
    g.add_node("generate", generate)
    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)
    return g.compile()
