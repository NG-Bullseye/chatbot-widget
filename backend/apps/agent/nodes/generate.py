from apps.agent.llm import get_llm
from apps.agent.prompts import build_system_prompt
from apps.agent.state import ChatState
from langchain_core.messages import SystemMessage


async def generate(state: ChatState) -> dict:
    """Call the LLM with the system prompt (incl. retrieved context) plus the
    conversation. Token streaming is captured at the app level via
    astream_events, so we just ainvoke here."""
    llm = get_llm(streaming=True)
    system = SystemMessage(content=build_system_prompt(state.get("context", "")))
    response = await llm.ainvoke([system, *state["messages"]])
    return {"messages": [response]}
