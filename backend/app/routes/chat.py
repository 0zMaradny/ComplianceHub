import json
import time
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse

from app.services.ai_chat import build_chat_context, chat_with_ai, chat_stream
from app.routes import _get_progress
from app.services import db
from app.services.ai import create_provider

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Chat"])

MODEL_MAP = {
    "claude-sonnet-4-6": "antigravity_claude_sonnet_46",
    "claude-opus-4-6-thinking": "antigravity_claude_opus_46",
}

FALLBACK_CHAIN = ["antigravity_claude_sonnet_46", "antigravity_claude_opus_46", "nemotron_ultra", "qwen3_coder", "groq_llama", "local_qwen3_4b"]


def _call_provider(provider_name: str, prompt: str, system_prompt: str | None = None,
                   temperature: float = 0.3, max_tokens: int = 4096) -> dict:
    try:
        provider = create_provider(provider_name)
        fn = provider.generate
        return fn(prompt, system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        return {"error": str(e)}


@router.post("/v1/chat/completions", summary="OpenAI-compatible chat completions endpoint")
async def openai_chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "claude-sonnet-4-6")
    temperature = body.get("temperature", 0.3)
    max_tokens = body.get("max_tokens", 4096)
    stream = body.get("stream", False)

    if not messages:
        raise HTTPException(status_code=400, detail="messages is required")

    system_prompt = None
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            system_prompt = content
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")

    prompt = "\n".join(prompt_parts) if prompt_parts else "..."

    if stream:
        async def event_stream():
            text = ""
            for pname in [MODEL_MAP.get(model)] + FALLBACK_CHAIN:
                if not pname:
                    continue
                result = _call_provider(pname, prompt, system_prompt, temperature, max_tokens)
                if "error" not in result or not result["error"]:
                    text = result.get("text", result.get("response", json.dumps(result)))
                    break
            if text:
                yield f"data: {json.dumps({'choices': [{'delta': {'content': text}, 'index': 0}]})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    text = ""
    error_msg = ""
    chain = [MODEL_MAP.get(model)] + FALLBACK_CHAIN if model in MODEL_MAP else FALLBACK_CHAIN
    for pname in chain:
        if not pname:
            continue
        result = _call_provider(pname, prompt, system_prompt, temperature, max_tokens)
        if "error" not in result or not result["error"]:
            text = result.get("text", result.get("response", json.dumps(result)))
            break
        error_msg = result.get("error", "unknown error")

    if not text:
        return JSONResponse(
            status_code=502,
            content={"error": {"message": error_msg, "type": "provider_error", "code": 502}},
        )

    response_id = f"chatcmpl-{int(time.time())}"
    return {
        "id": response_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt) // 4,
            "completion_tokens": len(text) // 4,
            "total_tokens": (len(prompt) + len(text)) // 4,
        },
    }


@router.post("/api/chat", summary="Chat with AI about generated documents")
async def chat_endpoint(request: Request):
    body = await request.json()
    job_id = body.get("job_id", "")
    message = body.get("message", "")
    history = body.get("history", [])
    if not job_id or not message:
        raise HTTPException(status_code=400, detail="job_id and message are required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    context = build_chat_context(job_data)
    result = chat_with_ai(message, context, history)
    return result


@router.post("/api/chat/stream", summary="Stream chat response via SSE")
async def chat_stream_endpoint(request: Request):
    body = await request.json()
    job_id = body.get("job_id", "")
    message = body.get("message", "")
    history = body.get("history", [])
    if not job_id or not message:
        raise HTTPException(status_code=400, detail="job_id and message are required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    context = build_chat_context(job_data)

    async def event_stream():
        for token in chat_stream(message, context, history):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type='text/event-stream')
