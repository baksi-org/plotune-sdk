# src/workers/produce_worker.py
import asyncio
import json
from aiohttp import ClientSession
from multiprocessing import Queue, Event as MpEvent
import time

def build_producer_url(username: str, stream_name: str) -> str:
    return f"wss://stream.plotune.net/ws/producer/{username}/{stream_name}"

def data_from_queue(q: Queue):
    try:
        data = q.get_nowait()
        if not isinstance(data, dict):
            return None
        
        return {
            "key": data.get("key", "Unknown"),
            "time": data.get("time", int(time.time())),
            "value": data.get("value", 0)
        }
    except:
        return None

async def producer_worker(username: str, stream_name: str, token: str, q: Queue, stop_event, interval: float = 0.2):
    url = build_producer_url(username, stream_name)
    
    while not stop_event.is_set():
        try:
            async with ClientSession() as session:
                async with session.ws_connect(
                    url,
                    headers={"Authorization": f"Bearer {token}"}
                ) as ws:
                    print(f"[PRODUCER] Connected to {url}")
                    
                    while not stop_event.is_set():
                        message = data_from_queue(q)
                        if message:
                            try:
                                await ws.send_str(json.dumps(message))
                                print(f"[PRODUCER] Sent: {message}")
                            except Exception as e:
                                print(f"[PRODUCER] Send error: {e}")
                                break
                        
                        await asyncio.sleep(interval)
                        
                        # Send a ping to keep connection alive
                        if not stop_event.is_set():
                            try:
                                await ws.ping()
                            except:
                                break
                                
        except Exception as e:
            if not stop_event.is_set():
                print(f"[PRODUCER] Connection error: {e}")
                await asyncio.sleep(1)  # Wait before reconnecting
            else:
                break
    
    print("[PRODUCER] Worker stopped")

def worker_entry(username: str, stream_name: str, token: str, q: Queue, stop_event = None, interval: float = 0.2):
    if stop_event is None:
        stop_event = MpEvent()
    
    asyncio.run(producer_worker(username, stream_name, token, q, stop_event, interval))