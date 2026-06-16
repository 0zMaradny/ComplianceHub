import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.services.ai_chat import build_chat_context, chat_with_ai, chat_stream
from app.routes import _get_progress
from app.services import db

router = APIRouter(tags=["AI Chat"])


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
