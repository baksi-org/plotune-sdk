import asyncio
import json
from aiohttp import ClientSession, WSMsgType
from multiprocessing import Queue, Event as MpEvent  # multiprocessing.Event

def build_url(username: str, stream_name: str, group: str) -> str:
    return f"wss://stream.plotune.net/ws/consumer/{username}/{stream_name}/{group}"

async def _put_to_queue_async(q: Queue, item):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, q.put, item)

async def consume(username: str, stream_name: str, group: str, token: str, q: Queue, stop_event):
    url = build_url(username, stream_name, group)
    try:
        async with ClientSession() as session:
            async with session.ws_connect(
                url,
                headers={"Authorization": f"Bearer {token}"}
            ) as ws:
                while not stop_event.is_set():
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=0.5)
                    except asyncio.CancelledError:
                        break
                    except asyncio.TimeoutError:
                        continue

                    if msg.type == WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await _put_to_queue_async(q, {"type": "message", "payload": data})
                    elif msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSING):
                        break
                    elif msg.type == WSMsgType.ERROR:
                        break

    except Exception as e:
        if not stop_event.is_set():
            pass#print(f"[{group}] Connection FAILED: {e}")
    finally:
        pass#print(f"[{group}] Worker exiting")

def worker_entry(username: str, stream_name: str, group: str, token: str, q: Queue, stop_event = None):
    if stop_event is None:
        stop_event = MpEvent()
    asyncio.run(consume(username, stream_name, group, token, q, stop_event))