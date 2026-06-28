import asyncio
import json
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings

router = APIRouter()


@router.websocket("/runs/{run_id}")
async def run_logs_ws(websocket: WebSocket, run_id: UUID):
    await websocket.accept()
    client = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = client.pubsub()
    channel = f"run:{run_id}:logs"
    await pubsub.subscribe(channel)

    async def reader():
        try:
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg and msg["type"] == "message":
                    data = json.loads(msg["data"])
                    await websocket.send_json(data)
                await asyncio.sleep(0.05)
        except WebSocketDisconnect:
            pass

    try:
        await reader()
    finally:
        await pubsub.unsubscribe(channel)
        await client.aclose()
