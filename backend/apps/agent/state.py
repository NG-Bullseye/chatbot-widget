from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """State that flows through the graph.

    messages: full conversation (history + new user turn). add_messages appends
              new messages instead of overwriting.
    context:  retrieved knowledge-base snippets, filled by the retrieve node.
    """

    messages: Annotated[list, add_messages]
    context: str
