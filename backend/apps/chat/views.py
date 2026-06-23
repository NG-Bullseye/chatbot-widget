import json

from apps.agent.graph import get_graph
from apps.agent.observability import get_callbacks
from asgiref.sync import sync_to_async
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from langchain_core.messages import AIMessage, HumanMessage

from .models import Conversation, Message


@sync_to_async
def _load_history(session_id: str):
    """Return (conversation, langchain message list) for the session."""
    conversation, _ = Conversation.objects.get_or_create(session_id=session_id)
    history = []
    for m in conversation.messages.all():
        cls = HumanMessage if m.role == Message.Role.USER else AIMessage
        history.append(cls(content=m.content))
    return conversation, history


@sync_to_async
def _persist(conversation, user_text: str, assistant_text: str):
    Message.objects.create(
        conversation=conversation, role=Message.Role.USER, content=user_text
    )
    Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=assistant_text,
    )


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@csrf_exempt
@require_POST
async def chat(request):
    """Streams the assistant answer token-by-token as Server-Sent Events.

    DB work (load history / persist) happens around the stream; the graph run
    in between stays free of sync ORM writes.
    """
    try:
        payload = json.loads(request.body)
        session_id = payload["session_id"]
        user_text = payload["message"].strip()
    except (KeyError, ValueError):
        return JsonResponse({"error": "session_id and message required"}, status=400)

    if not user_text:
        return JsonResponse({"error": "empty message"}, status=400)

    conversation, history = await _load_history(session_id)
    inputs = {"messages": [*history, HumanMessage(content=user_text)]}
    config = {"callbacks": get_callbacks(session_id=session_id)}

    async def event_stream():
        full = []
        graph = get_graph()
        try:
            async for event in graph.astream_events(inputs, config, version="v2"):
                # Only stream tokens from the generate node's chat model.
                if event["event"] == "on_chat_model_stream":
                    token = event["data"]["chunk"].content
                    if token:
                        full.append(token)
                        yield _sse({"type": "token", "content": token})
            answer = "".join(full)
            await _persist(conversation, user_text, answer)
            yield _sse({"type": "done"})
        except Exception as exc:  # surface errors to the widget instead of hanging
            yield _sse({"type": "error", "message": str(exc)})

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@csrf_exempt
@require_POST
async def feedback(request):
    """Forward a thumbs up/down to Langfuse as a session score."""
    try:
        payload = json.loads(request.body)
        session_id = payload["session_id"]
        score = int(payload["score"])  # 1 or -1
    except (KeyError, ValueError):
        return JsonResponse({"error": "session_id and score required"}, status=400)

    import os

    if os.environ.get("LANGFUSE_PUBLIC_KEY"):
        from langfuse import Langfuse

        lf = Langfuse()
        await sync_to_async(lf.score)(
            name="user_feedback",
            value=score,
            comment=payload.get("comment", ""),
            session_id=session_id,
        )
    return JsonResponse({"ok": True})
