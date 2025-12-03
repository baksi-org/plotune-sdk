import asyncio
import json
from aiohttp import ClientSession, WSMsgType
from multiprocessing import Queue, Event as MpEvent  # multiprocessing.Event

def build_url(username: str, stream_name: str) -> str:
    return f"wss://stream.plotune.net/ws/producer/{username}/{stream_name}"

def data_from_queue(q:Queue):
    data = q.get(True)
    if not isinstance(data, dict):
        return None
    
    return {"key":data.get("key","Unknown"), "time":data.get("time",0), "value":data.get("value", 0)}

async def producer_worker(username: str, stream_name: str, token: str, q: Queue, stop_event, interval:float):
    url = build_url(username, stream_name)
    async with ClientSession() as session:
        async with session.ws_connect(
            url, 
            headers={"Authorization": f"Bearer {token}"}
        ) as ws:
            while not stop_event.is_set():
                message = data_from_queue(q)
                if not message:
                    continue
                await ws.send_str(json.dumps(message))
                await asyncio.sleep(interval)


def worker_entry(username: str, stream_name: str, group: str, token: str, q: Queue, stop_event = None, interval:float=1/5 ):
    if stop_event is None:
        stop_event = MpEvent()
    asyncio.run(producer_worker(username, stream_name, group, token, q, stop_event, interval))