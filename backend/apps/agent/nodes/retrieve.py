from apps.agent.state import ChatState
from apps.knowledge.retrieval import similar_chunks
from langchain_core.messages import HumanMessage


async def retrieve(state: ChatState) -> dict:
    """RAG step: take the latest user message, fetch the most similar
    knowledge-base chunks via pgvector, and put them into state.context.

    Read-only async DB access only -- no ORM writes happen inside the graph.
    """
    last_user = next(
        (m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        None,
    )
    if last_user is None:
        return {"context": ""}

    chunks = await similar_chunks(last_user.content, k=4)
    context = "\n\n".join(c.content for c in chunks)
    return {"context": context}
